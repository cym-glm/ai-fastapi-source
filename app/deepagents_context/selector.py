from app.deepagents_context.compressor import SimpleContextCompressor
from app.deepagents_context.schemas import (
    ContextBudget,
    ContextItem,
    ContextPlacement,
    ContextPriority,
)


class ContextSelector:
    def __init__(self):
        self.compressor = SimpleContextCompressor()

    def prepare_items(
        self,
        items: list[ContextItem],
    ) -> list[ContextItem]:
        for item in items:
            item.estimated_tokens = self.compressor.estimate_tokens(
                item.summary or item.content
            )

        return items

    def select(
        self,
        items: list[ContextItem],
        budget: ContextBudget,
    ) -> tuple[list[ContextItem], list[ContextItem], list[ContextItem], list[str]]:
        """
        返回：
        active_items, offloaded_items, dropped_items, warnings
        """
        warnings: list[str] = []

        prepared = self.prepare_items(items)

        priority_order = {
            ContextPriority.CRITICAL: 0,
            ContextPriority.HIGH: 1,
            ContextPriority.MEDIUM: 2,
            ContextPriority.LOW: 3,
        }

        prepared.sort(
            key=lambda item: (
                priority_order[item.priority],
                item.estimated_tokens,
            )
        )

        active: list[ContextItem] = []
        offloaded: list[ContextItem] = []
        dropped: list[ContextItem] = []

        remaining = budget.available_tokens

        for item in prepared:
            active_text = item.summary or item.content
            token_count = self.compressor.estimate_tokens(active_text)

            if item.priority == ContextPriority.CRITICAL:
                item.placement = ContextPlacement.ACTIVE_CONTEXT
                active.append(item)
                remaining -= token_count

                if remaining < 0:
                    warnings.append(
                        "CRITICAL 上下文已超过预算，需要提高 max_tokens 或压缩系统提示词。"
                    )

                continue

            if token_count <= remaining:
                item.placement = ContextPlacement.ACTIVE_CONTEXT
                active.append(item)
                remaining -= token_count
                continue

            if item.file_path:
                item.placement = ContextPlacement.WORKSPACE_FILE
                offloaded.append(item)
                warnings.append(
                    f"上下文已 offload 到文件：{item.file_path}"
                )
                continue

            if item.priority in [
                ContextPriority.HIGH,
                ContextPriority.MEDIUM,
            ]:
                compressed = self.compressor.summarize(
                    item.content,
                    max_chars=500,
                )
                compressed_tokens = self.compressor.estimate_tokens(
                    compressed
                )

                if compressed_tokens <= remaining:
                    item.summary = compressed
                    item.placement = ContextPlacement.ACTIVE_CONTEXT
                    active.append(item)
                    remaining -= compressed_tokens
                    warnings.append(
                        f"上下文已压缩：{item.title or item.item_id}"
                    )
                    continue

            item.placement = ContextPlacement.DROPPED
            dropped.append(item)
            warnings.append(
                f"上下文已丢弃：{item.title or item.item_id}"
            )

        return active, offloaded, dropped, warnings