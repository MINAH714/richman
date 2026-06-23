from stocks.services.dashboard import KOREAN_DASHBOARD_SEED_STOCKS

# 종목명 → 티커 딕셔너리 생성
KOREAN_STOCK_DICT = {
    item["name"].lower(): item["symbol"]
    for item in KOREAN_DASHBOARD_SEED_STOCKS
}


def convert_to_stock_symbol(name: str):
    """
    삼성전자 -> 005930.KS
    SK하이닉스 -> 000660.KS
    카카오 -> 035720.KS
    """

    if not name:
        return None

    return KOREAN_STOCK_DICT.get(name.lower())