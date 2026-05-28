import requests
from typing import Optional

UPBIT_BASE_URL = "https://api.upbit.com/v1"

def get_all_krw_markets() -> list[dict]:
    """KRW 마켓 코인 목록 전체 조회"""
    res = requests.get(f"{UPBIT_BASE_URL}/market/all", params={"isDetails": "false"})
    res.raise_for_status()
    markets = res.json()
    return [m for m in markets if m["market"].startswith("KRW-")]

def get_ticker(markets: list[str]) -> list[dict]:
    """
    실시간 시세 조회 (여러 마켓 한 번에)
    markets: ["KRW-BTC", "KRW-ETH", ...]
    """
    market_str = ",".join(markets)
    res = requests.get(f"{UPBIT_BASE_URL}/ticker", params={"markets": market_str})
    res.raise_for_status()
    return res.json()

def get_candles_days(market: str, count: int = 30) -> list[dict]:
    """일봉 캔들 데이터 조회 (차트용)"""
    res = requests.get(
        f"{UPBIT_BASE_URL}/candles/days",
        params={"market": market, "count": count}
    )
    res.raise_for_status()
    return res.json()