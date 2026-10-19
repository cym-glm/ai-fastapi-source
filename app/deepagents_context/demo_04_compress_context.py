from app.deepagents_context.compressor import SimpleContextCompressor


def main():
    compressor = SimpleContextCompressor()

    text = """
这是第一段普通描述。
核心结论：Context 管理不能把所有信息塞进 Prompt。
这是第二段普通描述。
风险：长工具结果会导致上下文爆炸。
这是第三段普通描述。
建议：长内容写入 workspace，只把摘要放进 active context。
失败：如果上下文过长，模型可能忽略用户当前目标。
"""

    print("original:")
    print(text)

    print("=" * 80)
    print("estimated_tokens:", compressor.estimate_tokens(text))

    print("=" * 80)
    print("summary:")
    print(
        compressor.summarize(
            text,
            max_chars=300,
        )
    )


if __name__ == "__main__":
    main()