import uuid

from app.deep_research_agent.schemas import (
    ResearchSource,
    ResearchSourceType,
)


class ResearchSourceFactory:
    def create_web_source(
        self,
        title: str,
        content: str,
        url: str | None = None,
        score: float = 0.8,
    ) -> ResearchSource:
        return ResearchSource(
            source_id=f"src_web_{uuid.uuid4().hex[:10]}",
            source_type=ResearchSourceType.WEB,
            title=title,
            content=content,
            url=url,
            score=score,
        )

    def create_kb_source(
        self,
        title: str,
        content: str,
        file_path: str | None = None,
        score: float = 0.85,
    ) -> ResearchSource:
        return ResearchSource(
            source_id=f"src_kb_{uuid.uuid4().hex[:10]}",
            source_type=ResearchSourceType.ENTERPRISE_KB,
            title=title,
            content=content,
            file_path=file_path,
            score=score,
        )


class ResearchSourceDeduplicator:
    def deduplicate(
        self,
        sources: list[ResearchSource],
    ) -> list[ResearchSource]:
        seen: set[str] = set()
        results: list[ResearchSource] = []

        for source in sources:
            key = self._normalize(source.title + source.content[:120])

            if key in seen:
                continue

            seen.add(key)
            results.append(source)

        return results

    def _normalize(
        self,
        text: str,
    ) -> str:
        return (
            text.lower()
            .replace(" ", "")
            .replace("\n", "")
            .replace("\t", "")
        )