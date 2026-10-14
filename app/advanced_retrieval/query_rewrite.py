import re

from app.advanced_retrieval.schemas import (
    MultiQueryResult,
    QueryRewriteResult,
)


class RuleBasedQueryRewriter:
    """
    教学版 Query Rewrite。

    说明：
    生产环境可以替换成 LLM + Structured Output。
    """

    def rewrite(
        self,
        query: str,
    ) -> QueryRewriteResult:
        normalized = query.strip()

        intent = "general"
        keywords: list[str] = []
        filters: dict[str, str] = {}

        if any(word in normalized for word in ["退钱", "退款", "不想要", "取消订单"]):
            intent = "refund"
            keywords.extend(["退款", "取消订单", "未发货", "售后"])
            filters["doc_type"] = "after_sales"

        elif any(word in normalized for word in ["快递", "物流", "配送", "没动"]):
            intent = "logistics"
            keywords.extend(["物流", "快递", "配送", "更新"])
            filters["doc_type"] = "logistics"

        elif any(word in normalized for word in ["发票", "抬头", "纳税人"]):
            intent = "invoice"
            keywords.extend(["发票", "企业", "个人", "纳税人识别号"])
            filters["doc_type"] = "invoice"

        elif any(word in normalized for word in ["年假", "请假", "休假"]):
            intent = "leave"
            keywords.extend(["年假", "请假", "员工手册"])
            filters["doc_type"] = "employee_handbook"

        elif any(word in normalized for word in ["报销", "差旅", "行程单"]):
            intent = "reimbursement"
            keywords.extend(["报销", "差旅", "发票", "审批记录"])
            filters["doc_type"] = "employee_handbook"

        rewritten_query = self._build_rewritten_query(
            original_query=normalized,
            intent=intent,
            keywords=keywords,
        )

        return QueryRewriteResult(
            original_query=query,
            rewritten_query=rewritten_query,
            intent=intent,
            keywords=keywords,
            filters=filters,
        )

    def _build_rewritten_query(
        self,
        original_query: str,
        intent: str,
        keywords: list[str],
    ) -> str:
        if intent == "refund":
            return "订单未发货取消订单退款规则 退款到账时间 售后规则"

        if intent == "logistics":
            return "物流配送进度 快递超过 7 天未更新 客服核查"

        if intent == "invoice":
            return "电子发票 企业发票 抬头 纳税人识别号"

        if intent == "leave":
            return "员工手册 年假制度 年假申请 条件"

        if intent == "reimbursement":
            return "差旅报销 发票 行程单 审批记录 报销制度"

        if keywords:
            return f"{original_query} {' '.join(keywords)}"

        return original_query


class RuleBasedMultiQueryExpander:
    def expand(
        self,
        query: str,
        rewrite_result: QueryRewriteResult | None = None,
    ) -> MultiQueryResult:
        queries = [query]

        if rewrite_result:
            queries.append(rewrite_result.rewritten_query)

            if rewrite_result.intent == "refund":
                queries.extend([
                    "未发货订单可以退款吗",
                    "取消订单退款流程",
                    "退款审核通过后多久到账",
                ])

            elif rewrite_result.intent == "logistics":
                queries.extend([
                    "物流超过 7 天没有更新怎么办",
                    "如何查询快递配送进度",
                ])

            elif rewrite_result.intent == "invoice":
                queries.extend([
                    "企业发票需要填写什么",
                    "电子发票申请规则",
                ])

            elif rewrite_result.intent == "leave":
                queries.extend([
                    "员工入职多久可以申请年假",
                    "年假制度",
                ])

            elif rewrite_result.intent == "reimbursement":
                queries.extend([
                    "差旅报销需要什么材料",
                    "报销需要发票和审批记录吗",
                ])

        # 去重并保持顺序。
        deduped = []
        seen = set()

        for item in queries:
            cleaned = re.sub(r"\s+", " ", item.strip())

            if cleaned and cleaned not in seen:
                deduped.append(cleaned)
                seen.add(cleaned)

        return MultiQueryResult(
            original_query=query,
            queries=deduped,
        )