import yfinance as yf


def get_stock_summary(symbol):
    """
    챗봇용 주식 데이터 반환
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info

        return {
            "symbol": symbol,
            "current_price": info.get("lastPrice") or info.get("last_price"),
            "day_high": info.get("dayHigh"),
            "day_low": info.get("dayLow"),
            "year_high": info.get("yearHigh"),
            "year_low": info.get("yearLow"),
        }

    except Exception:
        return {}