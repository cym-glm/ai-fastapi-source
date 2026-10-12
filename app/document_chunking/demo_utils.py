from app.document_chunking.schemas import ChunkResult


def print_chunk_result(
    result: ChunkResult,
):
    print("document_id:", result.document_id)
    print("title:", result.title)
    print("strategy:", result.strategy)
    print("total_chunks:", result.total_chunks)

    if result.warnings:
        print("warnings:")
        for warning in result.warnings:
            print("-", warning)

    print("=" * 80)

    for chunk in result.chunks:
        print("chunk_id:", chunk.chunk_id)
        print("chunk_index:", chunk.chunk_index)
        print("strategy:", chunk.strategy)
        print("content:")
        print(chunk.content)
        print("metadata:")
        print(chunk.metadata)
        print("-" * 80)