from app.advanced_retrieval.schemas import HybridSearchResult


class RAGContextBuilder:
    def build_context(
        self,
        results: list[HybridSearchResult],
        max_chars: int = 2000,
    ) -> tuple[str, list[dict]]:
        context_parts: list[str] = []
        sources: list[dict] = []
        used_chars = 0

        for index, item in enumerate(results, start=1):
            source = {
                "chunk_id": item.chunk_id,
                "document_id": item.document_id,
                "document_title": item.metadata.get("document_title") or item.metadata.get("title"),
                "source_path": item.metadata.get("source_path"),
                "page_number": item.metadata.get("page_number"),
                "page_numbers": item.metadata.get("page_numbers"),
                "heading": item.metadata.get("heading"),
                "score": item.final_score,
                "matched_by": item.matched_by,
            }

            content = item.content.strip()

            part = (
                f"资料 {index}：\n"
                f"来源：{source.get('source_path')}\n"
                f"标题：{source.get('heading') or source.get('document_title')}\n"
                f"匹配方式：{','.join(item.matched_by)}\n"
                f"分数：{item.final_score:.4f}\n"
                f"内容：{content}"
            )

            if used_chars + len(part) > max_chars:
                break

            context_parts.append(part)
            sources.append(source)
            used_chars += len(part)

        context = "\n\n".join(context_parts)

        return context, sources