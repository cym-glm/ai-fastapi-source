import re


class TextCleaner:
    def clean_text(
        self,
        text: str,
    ) -> str:
        if not text:
            return ""

        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # 去掉过多空格。
        text = re.sub(r"[ \t]+", " ", text)

        # 连续 3 个以上换行压缩成 2 个。
        text = re.sub(r"\n{3,}", "\n\n", text)

        # 去掉每行首尾空格。
        lines = [
            line.strip()
            for line in text.split("\n")
        ]

        text = "\n".join(lines)

        return text.strip()

    def remove_repeated_lines(
        self,
        text: str,
        min_repeat: int = 3,
    ) -> str:
        """
        简单去除重复页眉页脚。

        说明：
        如果同一行在文档中重复出现很多次，可能是页眉页脚。
        这里只做教学版规则，生产环境要谨慎。
        """
        lines = [
            line.strip()
            for line in text.split("\n")
            if line.strip()
        ]

        counter: dict[str, int] = {}

        for line in lines:
            counter[line] = counter.get(line, 0) + 1

        cleaned_lines = [
            line for line in lines
            if counter.get(line, 0) < min_repeat
        ]

        return "\n".join(cleaned_lines)