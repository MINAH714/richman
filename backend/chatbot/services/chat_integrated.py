import json

from consumption.services.chat_consumption import (
    get_monthly_consumption_summary
)

from finlife.services.chat_finlife import (
    get_finlife_summary
)

from stocks.services.chat_stock import get_stock_summary
from crypto.services.upbit import get_ticker


def get_integrated_context(user):

    context_data = {}

    try:
        context_data["consumption"] = (
            get_monthly_consumption_summary(user)
        )
    except Exception:
        context_data["consumption"] = {}

    try:
        context_data["finlife"] = (
            get_finlife_summary()
        )
    except Exception:
        context_data["finlife"] = {}

    # 대표 주식
    try:
        context_data["stock"] = {
            "삼성전자": get_stock_summary("005930.KS"),
            "애플": get_stock_summary("AAPL")
        }
    except Exception:
        context_data["stock"] = {}

    try:
        btc = get_ticker(["KRW-BTC"])

        if btc:
            context_data["crypto"] = {
                "BTC": {
                    "trade_price": btc[0]["trade_price"],
                    "change_rate": round(
                        btc[0]["change_rate"] * 100,
                        2
                    )
                }
            }
        else:
            context_data["crypto"] = {}

    except Exception:
        context_data["crypto"] = {}

    return context_data