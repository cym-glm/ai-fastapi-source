from app.rag_principles.schemas import ChunkDocument, RawDocument


class SimpleTextSplitter:
    def __init__(
        self,
        chunk_size: int = 60,
        chunk_overlap: int = 10,
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size 必须大于 0")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap 不能小于 0")

        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap 必须小于 chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_document(
        self,
        document: RawDocument,
    ) -> list[ChunkDocument]:
        text = document.content
        chunks: list[ChunkDocument] = []

        start = 0
        chunk_index = 0

        while start < len(text):
            end = start + self.chunk_size
            content = text[start:end]

            chunk = ChunkDocument(
                chunk_id=f"{document.document_id}_chunk_{chunk_index}",
                document_id=document.document_id,
                title=document.title,
                content=content,
                metadata={
                    **document.metadata,
                    "chunk_index": chunk_index,
                },
            )

            chunks.append(chunk)

            if end >= len(text):
                break

            start = end - self.chunk_overlap
            chunk_index += 1

        return chunks

    def split_documents(
        self,
        documents: list[RawDocument],
    ) -> list[ChunkDocument]:
        all_chunks: list[ChunkDocument] = []

        for document in documents:
            all_chunks.extend(
                self.split_document(document)
            )

        return all_chunks