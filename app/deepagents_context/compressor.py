class SimpleContextCompressor:
    """
    教学版上下文压缩器。

    生产环境可以替换成：
    1. LLM summarizer
    2. Map-reduce summary
    3. Embedding-based extractive summary
    4. Rule-based key point extractor
    """

    def estimate_tokens(
        self,
        text: str,
    ) -> int:
        if not text:
            return 0

        # 教学版粗略估算：
        # 中文按 1.5 字符约等于 1 token，
        # 英文按 4 字符约等于 1 token。
        chinese_chars = sum(
            1 for char in text
            if "\u4e00" <= char <= "\u9fff"
        )
        other_chars = len(text) - chinese_chars

        return int(chinese_chars / 1.5 + other_chars / 4) + 1

    def summarize(
        self,
        text: str,
        max_chars: int = 600,
    ) -> str:
        if len(text) <= max_chars:
            return text

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        important_lines = []

        for line in lines:
            if any(keyword in line for keyword in [
                "结论",
                "风险",
                "建议",
                "问题",
                "核心",
                "摘要",
                "来源",
                "TODO",
                "失败",
                "成功",
            ]):
                important_lines.append(line)

        if not important_lines:
            important_lines = lines[:8]

        summary = "\n".join(
            f"- {line[:120]}"
            for line in important_lines[:10]
        )

        if len(summary) > max_chars:
            summary = summary[:max_chars] + "..."

        return (
            "【压缩摘要】\n"
            + summary
        )

    def truncate(
        self,
        text: str,
        max_chars: int,
    ) -> str:
        if len(text) <= max_chars:
            return text

        return text[:max_chars] + "\n\n...【内容已截断】"