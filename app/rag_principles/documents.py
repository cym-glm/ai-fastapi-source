from app.rag_principles.schemas import RawDocument


def load_mock_documents() -> list[RawDocument]:
    return [
        RawDocument(
            document_id="doc_after_sales",
            title="电商售后规则",
            content=(
                "订单未发货时，用户可以申请取消订单并退款。"
                "退款通常会在审核通过后 1 到 3 个工作日原路返回。"
                "订单已发货后，用户需要收到商品后再发起退货退款申请。"
                "如果商品存在质量问题，用户可以提交照片或视频凭证申请售后。"
            ),
            metadata={
                "department": "customer_service",
                "doc_type": "after_sales",
                "version": "2026-08",
            },
        ),
        RawDocument(
            document_id="doc_logistics",
            title="物流说明",
            content=(
                "订单发货后，用户可以通过物流单号查询配送进度。"
                "普通快递通常 3 到 5 天送达，偏远地区可能需要更长时间。"
                "如果物流超过 7 天没有更新，建议联系客服协助核查。"
            ),
            metadata={
                "department": "customer_service",
                "doc_type": "logistics",
                "version": "2026-08",
            },
        ),
        RawDocument(
            document_id="doc_invoice",
            title="发票规则",
            content=(
                "用户可以在订单完成后申请开具电子发票。"
                "发票抬头可以选择个人或企业。"
                "企业发票需要填写公司名称和纳税人识别号。"
            ),
            metadata={
                "department": "finance",
                "doc_type": "invoice",
                "version": "2026-08",
            },
        ),
    ]