from finlife.models import DepositProduct


def get_finlife_summary():
    """
    챗봇용 예금 상품 요약
    """

    products = DepositProduct.objects.prefetch_related(
        "options"
    )[:5]

    result = []

    for product in products:

        max_rate = None

        if product.options.exists():
            max_rate = max(
                option.intr_rate2 or option.intr_rate or 0
                for option in product.options.all()
            )

        result.append({
            "bank": product.kor_co_nm,
            "product_name": product.fin_prdt_nm,
            "join_way": product.join_way,
            "special_condition": product.spcl_cnd,
            "max_rate": max_rate
        })

    return {
        "products": result
    }