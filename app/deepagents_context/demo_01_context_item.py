from dataclasses import asdict

from app.deepagents_context.compressor import SimpleContextCompressor
from app.deepagents_context.schemas import (
    ContextItem,
    ContextPriority,
    ContextSource,
)


def main():
    compressor = SimpleContextCompressor()

    item = ContextItem(
        item_id="rag_001",
        source=ContextSource.RAG,
        priority=ContextPriority.HIGH,
        title="RAG 召回片段",
        content="DeepAgents Context 管理需要区分 messages、files、memory 和 store。",
    )

    item.estimated_tokens = compressor.estimate_tokens(
        item.content
    )

    print(asdict(item))


if __name__ == "__main__":
    main()