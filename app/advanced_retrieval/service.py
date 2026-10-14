from app.advanced_retrieval.context_builder import RAGContextBuilder
from app.advanced_retrieval.hybrid_search import HybridRetriever
from app.advanced_retrieval.keyword_search import SimpleKeywordSearchEngine
from app.advanced_retrieval.mmr import MMRSelector
from app.advanced_retrieval.query_rewrite import (
    RuleBasedMultiQueryExpander,
    RuleBasedQueryRewriter,
)
from app.advanced_retrieval.reranker import SimpleRuleReranker
from app.advanced_retrieval.schemas import (
    AdvancedRetrievalRequest,
    AdvancedRetrievalResponse,
    HybridSearchResult,
    RetrievalConfig,
)
from app.document_chunking.schemas import ChunkDocument, ChunkStrategy
from app.vector_knowledge.service import VectorKnowledgeService


class AdvancedRetrievalService:
    def __init__(self):
        self.vector_service = VectorKnowledgeService()
        self.keyword_engine = SimpleKeywordSearchEngine()
        self.query_rewriter = RuleBasedQueryRewriter()
        self.multi_query_expander = RuleBasedMultiQueryExpander()
        self.hybrid_retriever = HybridRetriever(
            vector_service=self.vector_service,
            keyword_engine=self.keyword_engine,
        )
        self.mmr_selector = MMRSelector(
            vector_service=self.vector_service,
        )
        self.reranker = SimpleRuleReranker()
        self.context_builder = RAGContextBuilder()

    def index_chunks(
        self,
        chunks: list[ChunkDocument],
    ) -> None:
        embedded_chunks = self.vector_service.embedding_service.embed_chunks(
            chunks
        )

        self.vector_service.vector_store.add_many(
            embedded_chunks
        )

        self.keyword_engine.add_many(
            embedded_chunks
        )

    def clear_index(self) -> None:
        self.vector_service.clear_index()
        self.keyword_engine.clear()

    def retrieve(
        self,
        request: AdvancedRetrievalRequest,
    ) -> AdvancedRetrievalResponse:
        query = request.query
        config = request.config

        rewrite_result = None
        rewritten_query = query
        merged_filters = dict(config.metadata_filter or {})

        if config.use_query_rewrite:
            rewrite_result = self.query_rewriter.rewrite(query)
            rewritten_query = rewrite_result.rewritten_query

            # 教学策略：
            # 如果用户没有显式传 metadata_filter，则使用 rewrite 推断出的 filter。
            if not config.metadata_filter and rewrite_result.filters:
                merged_filters.update(rewrite_result.filters)

        effective_config = RetrievalConfig(
            mode=config.mode,
            top_k=config.top_k,
            candidate_k=config.candidate_k,
            vector_weight=config.vector_weight,
            keyword_weight=config.keyword_weight,
            use_query_rewrite=config.use_query_rewrite,
            use_multi_query=config.use_multi_query,
            use_mmr=config.use_mmr,
            use_rerank=config.use_rerank,
            min_score=config.min_score,
            max_context_chars=config.max_context_chars,
            metadata_filter=merged_filters or None,
        )

        queries = [rewritten_query]

        if config.use_multi_query:
            expanded = self.multi_query_expander.expand(
                query=query,
                rewrite_result=rewrite_result,
            )
            queries = expanded.queries

        candidates = self._retrieve_multi_queries(
            queries=queries,
            config=effective_config,
        )

        candidates = self._deduplicate_results(candidates)

        if config.use_mmr:
            candidates = self.mmr_selector.select(
                query=rewritten_query,
                candidates=candidates,
                top_k=min(config.candidate_k, len(candidates)),
                lambda_mult=0.7,
            )

        if config.use_rerank:
            final_results = self.reranker.rerank(
                query=rewritten_query,
                candidates=candidates,
                top_k=config.top_k,
            )
        else:
            final_results = candidates[:config.top_k]

        fallback_reason = None

        if not final_results:
            fallback_reason = "no_retrieval_results"
        elif final_results[0].final_score < config.min_score:
            fallback_reason = "top_score_below_threshold"

        if fallback_reason:
            context = ""
            sources = []
        else:
            context, sources = self.context_builder.build_context(
                results=final_results,
                max_chars=config.max_context_chars,
            )

        return AdvancedRetrievalResponse(
            original_query=query,
            rewritten_query=rewritten_query,
            queries=queries,
            results=[] if fallback_reason else final_results,
            context=context,
            sources=sources,
            fallback_reason=fallback_reason,
            debug={
                "candidate_count": len(candidates),
                "metadata_filter": effective_config.metadata_filter,
                "use_query_rewrite": config.use_query_rewrite,
                "use_multi_query": config.use_multi_query,
                "use_mmr": config.use_mmr,
                "use_rerank": config.use_rerank,
            },
        )

    def _retrieve_multi_queries(
        self,
        queries: list[str],
        config: RetrievalConfig,
    ) -> list[HybridSearchResult]:
        all_results: list[HybridSearchResult] = []

        for query in queries:
            results = self.hybrid_retriever.retrieve(
                query=query,
                config=config,
            )
            all_results.extend(results)

        all_results.sort(
            key=lambda item: item.final_score,
            reverse=True,
        )

        return all_results

    def _deduplicate_results(
        self,
        results: list[HybridSearchResult],
    ) -> list[HybridSearchResult]:
        merged: dict[str, HybridSearchResult] = {}

        for item in results:
            existing = merged.get(item.chunk_id)

            if not existing:
                merged[item.chunk_id] = item
                continue

            existing.final_score = max(
                existing.final_score,
                item.final_score,
            )
            existing.vector_score = max(
                existing.vector_score,
                item.vector_score,
            )
            existing.keyword_score = max(
                existing.keyword_score,
                item.keyword_score,
            )

            for source in item.matched_by:
                if source not in existing.matched_by:
                    existing.matched_by.append(source)

        deduped = list(merged.values())
        deduped.sort(
            key=lambda item: item.final_score,
            reverse=True,
        )

        return deduped


def build_sample_chunks() -> list[ChunkDocument]:
    return [
        ChunkDocument(
            chunk_id="after_sales_001",
            document_id="doc_after_sales",
            title="电商售后规则",
            content="订单未发货时，用户可以申请取消订单并退款。退款通常会在审核通过后 1 到 3 个工作日原路返回。",
            chunk_index=0,
            strategy=ChunkStrategy.PARAGRAPH,
            metadata={
                "tenant_id": "tenant_001",
                "doc_type": "after_sales",
                "source_path": "data/sample_docs/after_sales.txt",
                "heading": "未发货退款规则",
                "is_latest": True,
            },
        ),
        ChunkDocument(
            chunk_id="after_sales_002",
            document_id="doc_after_sales",
            title="电商售后规则",
            content="订单已发货后，用户需要收到商品后再发起退货退款申请。如果商品存在质量问题，可以提交照片或视频凭证。",
            chunk_index=1,
            strategy=ChunkStrategy.PARAGRAPH,
            metadata={
                "tenant_id": "tenant_001",
                "doc_type": "after_sales",
                "source_path": "data/sample_docs/after_sales.txt",
                "heading": "已发货退货规则",
                "is_latest": True,
            },
        ),
        ChunkDocument(
            chunk_id="logistics_001",
            document_id="doc_logistics",
            title="物流说明",
            content="订单发货后，用户可以通过物流单号查询配送进度。如果物流超过 7 天没有更新，建议联系客服协助核查。",
            chunk_index=0,
            strategy=ChunkStrategy.PARAGRAPH,
            metadata={
                "tenant_id": "tenant_001",
                "doc_type": "logistics",
                "source_path": "data/sample_docs/logistics.txt",
                "heading": "物流异常处理",
                "is_latest": True,
            },
        ),
        ChunkDocument(
            chunk_id="invoice_001",
            document_id="doc_invoice",
            title="发票规则",
            content="用户可以在订单完成后申请开具电子发票。企业发票需要填写公司名称和纳税人识别号。",
            chunk_index=0,
            strategy=ChunkStrategy.PARAGRAPH,
            metadata={
                "tenant_id": "tenant_001",
                "doc_type": "invoice",
                "source_path": "data/sample_docs/invoice.txt",
                "heading": "发票申请规则",
                "is_latest": True,
            },
        ),
        ChunkDocument(
            chunk_id="employee_001",
            document_id="doc_employee_handbook",
            title="员工手册",
            content="员工入职满一年后，可以按照公司制度申请年假。年假申请需要提前提交审批。",
            chunk_index=0,
            strategy=ChunkStrategy.HEADING,
            metadata={
                "tenant_id": "tenant_001",
                "doc_type": "employee_handbook",
                "source_path": "data/sample_docs/employee_handbook.md",
                "heading": "年假制度",
                "department": "hr",
                "is_latest": True,
            },
        ),
        ChunkDocument(
            chunk_id="employee_002",
            document_id="doc_employee_handbook",
            title="员工手册",
            content="差旅报销需要提交发票、行程单和审批记录。报销申请需要按照公司流程提交。",
            chunk_index=1,
            strategy=ChunkStrategy.HEADING,
            metadata={
                "tenant_id": "tenant_001",
                "doc_type": "employee_handbook",
                "source_path": "data/sample_docs/employee_handbook.md",
                "heading": "报销制度",
                "department": "finance",
                "is_latest": True,
            },
        ),
    ]


advanced_retrieval_service = AdvancedRetrievalService()
advanced_retrieval_service.index_chunks(build_sample_chunks())