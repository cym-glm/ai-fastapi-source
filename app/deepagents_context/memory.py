from dataclasses import dataclass, field


@dataclass
class UserMemory:
    user_id: str
    preferences: list[str] = field(default_factory=list)
    project_terms: list[str] = field(default_factory=list)
    stable_facts: list[str] = field(default_factory=list)


class SimpleMemoryStore:
    """
    教学版长期记忆。

    注意：
    真实项目中不要随便存敏感信息。
    只保存用户明确同意、长期稳定、对后续任务有帮助的信息。
    """

    def __init__(self):
        self.memories: dict[str, UserMemory] = {}

    def get_or_create(
        self,
        user_id: str,
    ) -> UserMemory:
        if user_id not in self.memories:
            self.memories[user_id] = UserMemory(
                user_id=user_id
            )

        return self.memories[user_id]

    def add_preference(
        self,
        user_id: str,
        preference: str,
    ) -> None:
        memory = self.get_or_create(user_id)

        if preference not in memory.preferences:
            memory.preferences.append(preference)

    def add_project_term(
        self,
        user_id: str,
        term: str,
    ) -> None:
        memory = self.get_or_create(user_id)

        if term not in memory.project_terms:
            memory.project_terms.append(term)

    def add_stable_fact(
        self,
        user_id: str,
        fact: str,
    ) -> None:
        memory = self.get_or_create(user_id)

        if fact not in memory.stable_facts:
            memory.stable_facts.append(fact)

    def select_relevant_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
    ) -> list[str]:
        memory = self.get_or_create(user_id)

        candidates = (
            memory.preferences
            + memory.project_terms
            + memory.stable_facts
        )

        scored: list[tuple[int, str]] = []

        for item in candidates:
            score = self._score(item, query)

            if score > 0:
                scored.append((score, item))

        scored.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return [
            item for _score, item in scored[:limit]
        ]

    def _score(
        self,
        memory: str,
        query: str,
    ) -> int:
        score = 0

        for keyword in [
            "报告",
            "口语化",
            "代码",
            "RAG",
            "Agent",
            "DeepAgent",
            "面试",
            "简历",
            "企业知识库",
        ]:
            if keyword in memory and keyword in query:
                score += 2

        for char in set(query):
            if char in memory:
                score += 1

        return score


memory_store = SimpleMemoryStore()