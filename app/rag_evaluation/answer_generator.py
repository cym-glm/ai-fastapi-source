from app.advanced_retrieval.schemas import AdvancedRetrievalResponse


class SimpleGroundedAnswerGenerator:
    """
    教学版 Grounded Answer Generator。

    真实项目里这里会调用 LLM。
    本章为了让代码下载后直接运行，使用规则生成。
    """

    def generate(
        self,
        query: str,
        retrieval_response: AdvancedRetrievalResponse,
    ) -> str:
        if retrieval_response.fallback_reason:
            return "根据当前资料无法确认。"

        if not retrieval_response.results:
            return "根据当前资料无法确认。"

        best = retrieval_response.results[0]
        content = best.content

        if "未发货" in content and "退款" in content:
            return (
                "根据资料，订单未发货时，用户可以申请取消订单并退款。"
                "退款通常会在审核通过后 1 到 3 个工作日原路返回。"
            )

        if "已发货" in content and "退货" in content:
            return (
                "根据资料，订单已发货后，用户需要收到商品后再发起退货退款申请。"
                "如果商品存在质量问题，可以提交照片或视频凭证。"
            )

        if "物流超过 7 天" in content:
            return (
                "根据资料，如果物流超过 7 天没有更新，建议联系客服协助核查。"
            )

        if "企业发票" in content:
            return (
                "根据资料，企业发票需要填写公司名称和纳税人识别号。"
            )

        if "年假" in content:
            return (
                "根据资料，员工入职满一年后，可以按照公司制度申请年假。"
            )

        if "差旅报销" in content:
            return (
                "根据资料，差旅报销需要提交发票、行程单和审批记录。"
            )

        return f"根据资料，可以参考以下内容：{content}"