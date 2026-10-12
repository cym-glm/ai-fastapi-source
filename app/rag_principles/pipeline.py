from app.rag_principles.answer_generator import SimpleAnswerGenerator
from app.rag_principles.documents import load_mock_documents
from app.rag_principles.embedding import SimpleKeywordEmbedding
from app.rag_principles.prompt_builder import RAGPromptBuilder
from app.rag_principles.retriever import SimpleRetriever
from app.rag_principles.schemas import RAGAnswer
from app.rag_principles.splitter import SimpleTextSplitter
from app.rag_principles.vector_store import SimpleVectorStore


class MiniRAGPipeline:
    def __init__(self):
        self.embedding_model = SimpleKeywordEmbedding()
        self.vector_store = SimpleVectorStore()
        self.retriever = SimpleRetriever(
            embedding_model=self.embedding_model,
            vector_store=self.vector_store,
        )
        self.prompt_builder = RAGPromptBuilder()
        self.answer_generator = SimpleAnswerGenerator()

    def build_index(self) -> None:
        documents = load_mock_documents()

        splitter = SimpleTextSplitter(
            chunk_size=60,
            chunk_overlap=10,
        )

        chunks = splitter.split_documents(documents)

        embeddings = self.embedding_model.embed_documents(
            [
                chunk.content
                for chunk in chunks
            ]
        )

        self.vector_store.add_documents(
            chunks=chunks,
            embeddings=embeddings,
        )

    def ask(
        self,
        question: str,
        top_k: int = 3,
        metadata_filter: dict | None = None,
    ) -> RAGAnswer:
        retrieved_chunks = self.retriever.retrieve(
            query=question,
            top_k=top_k,
            metadata_filter=metadata_filter,
        )

        context = self.prompt_builder.build_context(
            retrieved_chunks
        )

        answer = self.answer_generator.generate(
            question=question,
            retrieved_chunks=retrieved_chunks,
        )

        return RAGAnswer(
            question=question,
            answer=answer,
            retrieved_chunks=retrieved_chunks,
            context=context,
        )