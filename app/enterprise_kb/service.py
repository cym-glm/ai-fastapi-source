import uuid
from dataclasses import asdict
from pathlib import Path

from app.advanced_retrieval.schemas import (
    AdvancedRetrievalRequest,
    RetrievalConfig,
    RetrievalMode,
)
from app.advanced_retrieval.service import AdvancedRetrievalService
from app.document_chunking.schemas import (
    ChunkConfig,
    ChunkStrategy,
)
from app.document_chunking.service import document_chunking_service
from app.document_parsing.service import document_parsing_service
from app.enterprise_kb.answer_generator import EnterpriseRAGAnswerGenerator
from app.enterprise_kb.repository import knowledge_repository
from app.enterprise_kb.schemas import (
    FeedbackRating,
    IndexFileResult,
    KnowledgeBaseStats,
    KnowledgeChatRequest,
    KnowledgeChatResponse,
    KnowledgeDocumentRecord,
    KnowledgeDocumentStatus,
    KnowledgeFeedback,
    KnowledgeQueryLog,
    KnowledgeSource,
)
from app.rag_evaluation.service import rag_evaluation_service


class EnterpriseKnowledgeBaseService:
    def __init__(self):
        self.repository = knowledge_repository
        self.retrieval_service = AdvancedRetrievalService()
        self.answer_generator = EnterpriseRAGAnswerGenerator()

    def index_file(
        self,
        file_path: str,
        tenant_id: str = "tenant_001",
        created_by: str = "system",
        doc_type: str | None = None,
        department: str | None = None,
        version: str = "v1",
        chunk_strategy: ChunkStrategy = ChunkStrategy.HEADING,
        chunk_size: int = 500,
        chunk_overlap: int = 80,
    ) -> IndexFileResult:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"文件不存在：{file_path}"
            )

        document_id = f"kb_doc_{uuid.uuid4().hex[:12]}"

        record = KnowledgeDocumentRecord(
            document_id=document_id,
            tenant_id=tenant_id,
            title=path.stem,
            file_name=path.name,
            file_path=str(path),
            file_type=path.suffix.lower(),
            status=KnowledgeDocumentStatus.UPLOADED,
            metadata={
                "tenant_id": tenant_id,
                "created_by": created_by,
                "doc_type": doc_type,
                "department": department,
                "version": version,
                "is_latest": True,
            },
        )

        self.repository.save_document(record)

        try:
            record.status = KnowledgeDocumentStatus.PARSING
            self.repository.save_document(record)

            parsed_document = document_parsing_service.parse_file(
                file_path=file_path,
                tenant_id=tenant_id,
                created_by=created_by,
            )

            # 统一覆盖 document_id，保证项目层 document_id 和 chunk 关联稳定。
            parsed_document.document_id = document_id
            parsed_document.metadata.update({
                "tenant_id": tenant_id,
                "created_by": created_by,
                "doc_type": doc_type,
                "department": department,
                "version": version,
                "is_latest": True,
            })

            if parsed_document.status.value in ["failed", "unsupported", "need_ocr"]:
                record.status = KnowledgeDocumentStatus.FAILED
                record.error_message = "; ".join(parsed_document.errors)
                self.repository.save_document(record)

                return IndexFileResult(
                    document=record,
                    chunk_count=0,
                    message="文档解析失败，未进入索引。",
                )

            record.status = KnowledgeDocumentStatus.CHUNKING
            self.repository.save_document(record)

            chunk_result = document_chunking_service.split_document(
                document=parsed_document,
                config=ChunkConfig(
                    strategy=chunk_strategy,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    min_chunk_size=10,
                ),
            )

            for chunk in chunk_result.chunks:
                chunk.metadata.update({
                    "tenant_id": tenant_id,
                    "doc_type": doc_type,
                    "department": department,
                    "version": version,
                    "is_latest": True,
                    "document_id": document_id,
                    "document_title": parsed_document.title,
                    "source_path": str(path),
                })

            record.status = KnowledgeDocumentStatus.EMBEDDING
            self.repository.save_document(record)

            self.retrieval_service.index_chunks(
                chunk_result.chunks
            )

            record.status = KnowledgeDocumentStatus.INDEXED
            record.chunk_count = len(chunk_result.chunks)
            record.title = parsed_document.title
            self.repository.save_document(record)

            return IndexFileResult(
                document=record,
                chunk_count=len(chunk_result.chunks),
                message="文档已完成解析、切分、向量化和索引。",
            )

        except Exception as exc:
            record.status = KnowledgeDocumentStatus.FAILED
            record.error_message = str(exc)
            self.repository.save_document(record)

            return IndexFileResult(
                document=record,
                chunk_count=0,
                message=f"文档入库失败：{exc}",
            )

    def chat(
        self,
        request: KnowledgeChatRequest,
    ) -> KnowledgeChatResponse:
        query_id = f"kb_query_{uuid.uuid4().hex[:12]}"

        metadata_filter = {
            "tenant_id": request.tenant_id,
        }

        if request.metadata_filter:
            metadata_filter.update(request.metadata_filter)

        retrieval_response = self.retrieval_service.retrieve(
            AdvancedRetrievalRequest(
                query=request.question,
                config=RetrievalConfig(
                    mode=RetrievalMode.HYBRID,
                    top_k=request.top_k,
                    candidate_k=10,
                    vector_weight=0.7,
                    keyword_weight=0.3,
                    use_query_rewrite=True,
                    use_multi_query=True,
                    use_mmr=True,
                    use_rerank=True,
                    min_score=0.01,
                    max_context_chars=1600,
                    metadata_filter=metadata_filter,
                ),
            )
        )

        answer = self.answer_generator.generate(
            question=request.question,
            retrieval_response=retrieval_response,
        )

        sources = [
            KnowledgeSource(
                chunk_id=item.chunk_id,
                document_id=item.document_id,
                source_path=item.metadata.get("source_path"),
                heading=item.metadata.get("heading"),
                page_number=item.metadata.get("page_number"),
                score=item.final_score,
                matched_by=item.matched_by,
            )
            for item in retrieval_response.results
        ]

        response = KnowledgeChatResponse(
            query_id=query_id,
            question=request.question,
            answer=answer,
            sources=sources,
            context=retrieval_response.context,
            fallback_reason=retrieval_response.fallback_reason,
            debug=retrieval_response.debug,
        )

        self.repository.save_query_log(
            KnowledgeQueryLog(
                query_id=query_id,
                tenant_id=request.tenant_id,
                user_id=request.user_id,
                question=request.question,
                answer=answer,
                retrieved_chunk_ids=[
                    source.chunk_id
                    for source in sources
                ],
                retrieved_scores=[
                    source.score
                    for source in sources
                ],
                sources=[
                    asdict(source)
                    for source in sources
                ],
                fallback_reason=retrieval_response.fallback_reason,
                metadata_filter=metadata_filter,
            )
        )

        return response

    def submit_feedback(
        self,
        query_id: str,
        tenant_id: str,
        user_id: str,
        rating: FeedbackRating,
        comment: str = "",
    ) -> KnowledgeFeedback:
        query_log = self.repository.get_query_log(query_id)

        if not query_log:
            raise ValueError(
                f"query_id 不存在：{query_id}"
            )

        feedback = KnowledgeFeedback(
            feedback_id=f"kb_feedback_{uuid.uuid4().hex[:12]}",
            query_id=query_id,
            tenant_id=tenant_id,
            user_id=user_id,
            rating=rating,
            comment=comment,
        )

        self.repository.save_feedback(feedback)

        return feedback

    def list_documents(
        self,
        tenant_id: str,
    ) -> list[KnowledgeDocumentRecord]:
        return self.repository.list_documents(
            tenant_id=tenant_id
        )

    def list_query_logs(
        self,
        tenant_id: str,
        limit: int = 20,
    ) -> list[KnowledgeQueryLog]:
        return self.repository.list_query_logs(
            tenant_id=tenant_id,
            limit=limit,
        )

    def list_feedbacks(
        self,
        tenant_id: str,
        limit: int = 20,
    ) -> list[KnowledgeFeedback]:
        return self.repository.list_feedbacks(
            tenant_id=tenant_id,
            limit=limit,
        )

    def get_stats(
        self,
        tenant_id: str,
    ) -> KnowledgeBaseStats:
        return KnowledgeBaseStats(
            document_count=self.repository.count_documents(tenant_id),
            indexed_document_count=self.repository.count_indexed_documents(tenant_id),
            query_count=self.repository.count_query_logs(tenant_id),
            feedback_count=self.repository.count_feedbacks(tenant_id),
        )

    def run_evaluation(self) -> dict:
        return rag_evaluation_service.run_full_report()


enterprise_kb_service = EnterpriseKnowledgeBaseService()