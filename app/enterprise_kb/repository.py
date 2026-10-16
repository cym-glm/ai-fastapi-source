from app.enterprise_kb.schemas import (
    KnowledgeDocumentRecord,
    KnowledgeFeedback,
    KnowledgeQueryLog,
)

# InMemoryKnowledgeRepository   plsql es  pgsql  

class InMemoryKnowledgeRepository:
    """
    教学版 Repository。

    说明：
    1. 本章为了代码可直接运行，使用内存保存。
    2. 生产环境请替换成 PostgreSQL / MySQL。
    """

    def __init__(self):
        self.documents: dict[str, KnowledgeDocumentRecord] = {}
        self.query_logs: dict[str, KnowledgeQueryLog] = {}
        self.feedbacks: dict[str, KnowledgeFeedback] = {}

    def save_document(
        self,
        document: KnowledgeDocumentRecord,
    ) -> None:
        self.documents[document.document_id] = document

    def get_document(
        self,
        document_id: str,
    ) -> KnowledgeDocumentRecord | None:
        return self.documents.get(document_id)

    def list_documents(
        self,
        tenant_id: str,
    ) -> list[KnowledgeDocumentRecord]:
        return [
            document for document in self.documents.values()
            if document.tenant_id == tenant_id
        ]

    def save_query_log(
        self,
        query_log: KnowledgeQueryLog,
    ) -> None:
        self.query_logs[query_log.query_id] = query_log

    def get_query_log(
        self,
        query_id: str,
    ) -> KnowledgeQueryLog | None:
        return self.query_logs.get(query_id)

    def list_query_logs(
        self,
        tenant_id: str,
        limit: int = 20,
    ) -> list[KnowledgeQueryLog]:
        logs = [
            log for log in self.query_logs.values()
            if log.tenant_id == tenant_id
        ]

        return logs[-limit:]

    def save_feedback(
        self,
        feedback: KnowledgeFeedback,
    ) -> None:
        self.feedbacks[feedback.feedback_id] = feedback

    def list_feedbacks(
        self,
        tenant_id: str,
        limit: int = 20,
    ) -> list[KnowledgeFeedback]:
        items = [
            feedback for feedback in self.feedbacks.values()
            if feedback.tenant_id == tenant_id
        ]

        return items[-limit:]

    def count_documents(
        self,
        tenant_id: str,
    ) -> int:
        return len(
            self.list_documents(tenant_id)
        )

    def count_indexed_documents(
        self,
        tenant_id: str,
    ) -> int:
        return len([
            document for document in self.documents.values()
            if document.tenant_id == tenant_id
            and document.status.value == "indexed"
        ])

    def count_query_logs(
        self,
        tenant_id: str,
    ) -> int:
        return len([
            log for log in self.query_logs.values()
            if log.tenant_id == tenant_id
        ])

    def count_feedbacks(
        self,
        tenant_id: str,
    ) -> int:
        return len([
            feedback for feedback in self.feedbacks.values()
            if feedback.tenant_id == tenant_id
        ])


knowledge_repository = InMemoryKnowledgeRepository()