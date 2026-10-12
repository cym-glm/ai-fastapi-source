from app.rag_principles.embedding import SimpleKeywordEmbedding
from app.rag_principles.schemas import RetrievedChunk
from app.rag_principles.vector_store import SimpleVectorStore


class SimpleRetriever:
    def __init__(
        self,
        embedding_model: SimpleKeywordEmbedding,
        vector_store: SimpleVectorStore,
    ):
        self.embedding_model = embedding_model
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        metadata_filter: dict | None = None,
    ) -> list[RetrievedChunk]:
        query_embedding = self.embedding_model.embed_query(query)

        return self.vector_store.similarity_search(
            query_embedding=query_embedding,
            top_k=top_k,
            metadata_filter=metadata_filter,
        )