import math

from app.rag_evaluation.schemas import (
    GeneratedAnswerForEval,
    RAGEvaluationCase,
    RetrievedItemForEval,
)


def calculate_hit_rate(
    expected_chunk_ids: list[str],
    retrieved_chunk_ids: list[str],
) -> float:
    if not expected_chunk_ids:
        return 1.0 if not retrieved_chunk_ids else 0.0

    expected_set = set(expected_chunk_ids)
    retrieved_set = set(retrieved_chunk_ids)

    return 1.0 if expected_set & retrieved_set else 0.0


def calculate_recall_at_k(
    expected_chunk_ids: list[str],
    retrieved_chunk_ids: list[str],
) -> float:
    if not expected_chunk_ids:
        return 1.0 if not retrieved_chunk_ids else 0.0

    expected_set = set(expected_chunk_ids)
    retrieved_set = set(retrieved_chunk_ids)

    return len(expected_set & retrieved_set) / len(expected_set)


def calculate_precision_at_k(
    expected_chunk_ids: list[str],
    retrieved_chunk_ids: list[str],
    k: int,
) -> float:
    if k <= 0:
        return 0.0

    if not retrieved_chunk_ids:
        return 1.0 if not expected_chunk_ids else 0.0

    expected_set = set(expected_chunk_ids)
    top_k = retrieved_chunk_ids[:k]

    if not top_k:
        return 0.0

    hit_count = sum(
        1 for chunk_id in top_k
        if chunk_id in expected_set
    )

    return hit_count / len(top_k)


def calculate_mrr(
    expected_chunk_ids: list[str],
    retrieved_chunk_ids: list[str],
) -> float:
    if not expected_chunk_ids:
        return 1.0 if not retrieved_chunk_ids else 0.0

    expected_set = set(expected_chunk_ids)

    for index, chunk_id in enumerate(retrieved_chunk_ids, start=1):
        if chunk_id in expected_set:
            return 1.0 / index

    return 0.0


def calculate_ndcg_at_k(
    expected_chunk_ids: list[str],
    retrieved_chunk_ids: list[str],
    k: int,
) -> float:
    if k <= 0:
        return 0.0

    if not expected_chunk_ids:
        return 1.0 if not retrieved_chunk_ids else 0.0

    expected_set = set(expected_chunk_ids)
    top_k = retrieved_chunk_ids[:k]

    dcg = 0.0

    for index, chunk_id in enumerate(top_k, start=1):
        relevance = 1.0 if chunk_id in expected_set else 0.0
        dcg += relevance / math.log2(index + 1)

    ideal_relevances = [1.0] * min(len(expected_set), k)
    idcg = 0.0

    for index, relevance in enumerate(ideal_relevances, start=1):
        idcg += relevance / math.log2(index + 1)

    if idcg == 0:
        return 0.0

    return dcg / idcg


def calculate_source_accuracy(
    expected_source_paths: list[str],
    retrieved_items: list[RetrievedItemForEval],
) -> float:
    if not expected_source_paths:
        return 1.0 if not retrieved_items else 0.0

    expected_set = set(expected_source_paths)

    retrieved_sources = {
        item.source_path
        for item in retrieved_items
        if item.source_path
    }

    return 1.0 if expected_set & retrieved_sources else 0.0


def calculate_keyword_coverage(
    expected_keywords: list[str],
    text: str,
) -> tuple[float, list[str]]:
    if not expected_keywords:
        return 1.0, []

    missing = [
        keyword
        for keyword in expected_keywords
        if keyword not in text
    ]

    coverage = (
        len(expected_keywords) - len(missing)
    ) / len(expected_keywords)

    return coverage, missing


def calculate_answer_relevance(
    case: RAGEvaluationCase,
    generated: GeneratedAnswerForEval,
) -> float:
    coverage, _missing = calculate_keyword_coverage(
        expected_keywords=case.expected_answer_keywords,
        text=generated.answer,
    )

    return coverage


def calculate_answer_correctness(
    case: RAGEvaluationCase,
    generated: GeneratedAnswerForEval,
) -> float:
    if not case.expected_answer:
        return calculate_answer_relevance(case, generated)

    expected_terms = _extract_terms(case.expected_answer)
    answer_terms = _extract_terms(generated.answer)

    if not expected_terms:
        return 1.0

    overlap = expected_terms & answer_terms

    return len(overlap) / len(expected_terms)


def calculate_context_relevance(
    case: RAGEvaluationCase,
    generated: GeneratedAnswerForEval,
) -> float:
    coverage, _missing = calculate_keyword_coverage(
        expected_keywords=case.expected_answer_keywords,
        text=generated.context,
    )

    return coverage


def calculate_citation_accuracy(
    case: RAGEvaluationCase,
    generated: GeneratedAnswerForEval,
) -> float:
    if not case.expected_source_paths:
        return 1.0 if not generated.sources else 0.0

    expected_set = set(case.expected_source_paths)

    source_paths = {
        source.get("source_path")
        for source in generated.sources
        if source.get("source_path")
    }

    return 1.0 if expected_set & source_paths else 0.0


def calculate_rule_based_faithfulness(
    generated: GeneratedAnswerForEval,
) -> tuple[float, list[str]]:
    """
    教学版 faithfulness。

    判断逻辑：
    1. 如果答案是“无法确认”，直接给 1。
    2. 如果答案里的关键句能在 context 中找到相似关键词，认为有依据。
    3. 如果出现明显过度承诺，扣分。
    """

    answer = generated.answer.strip()
    context = generated.context.strip()

    if not answer:
        return 0.0, ["答案为空"]

    if "无法确认" in answer:
        return 1.0, []

    if not context:
        return 0.0, ["没有检索上下文"]

    risky_claims = [
        "保证",
        "一定",
        "立即到账",
        "百分百",
        "无需审核",
    ]

    unsupported_claims = []

    for claim in risky_claims:
        if claim in answer and claim not in context:
            unsupported_claims.append(claim)

    answer_terms = _extract_terms(answer)
    context_terms = _extract_terms(context)

    if not answer_terms:
        return 1.0, unsupported_claims

    overlap = answer_terms & context_terms

    base_score = len(overlap) / len(answer_terms)

    penalty = 0.2 * len(unsupported_claims)

    score = max(0.0, min(1.0, base_score - penalty))

    return score, unsupported_claims


def _extract_terms(text: str) -> set[str]:
    business_terms = set()

    for term in [
        "订单",
        "未发货",
        "已发货",
        "退款",
        "退货",
        "售后",
        "物流",
        "快递",
        "7 天",
        "客服",
        "发票",
        "企业发票",
        "公司名称",
        "纳税人识别号",
        "年假",
        "入职满一年",
        "报销",
        "差旅报销",
        "行程单",
        "审批记录",
        "无法确认",
    ]:
        if term in text:
            business_terms.add(term)

    chinese_chars = {
        char for char in text
        if "\u4e00" <= char <= "\u9fff"
    }

    return business_terms | chinese_chars