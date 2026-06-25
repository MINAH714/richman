# crypto/services/upbit.py
import requests
from django.core.cache import cache

UPBIT_BASE_URL = "https://api.upbit.com/v1"
MARKETS_CACHE_KEY = "krw_markets"
MARKETS_CACHE_TTL = 600  # 10분


def get_all_krw_markets() -> list[dict]:
    """KRW 마켓 코인 목록 전체 조회 (10분 캐싱)"""
    cached = cache.get(MARKETS_CACHE_KEY)
    if cached:
        return cached

    res = requests.get(f"{UPBIT_BASE_URL}/market/all", params={"isDetails": "false"})
    res.raise_for_status()
    markets = res.json()
    krw_markets = [m for m in markets if m["market"].startswith("KRW-")]

    cache.set(MARKETS_CACHE_KEY, krw_markets, timeout=MARKETS_CACHE_TTL)
    return krw_markets


def get_ticker(markets: list[str]) -> list[dict]:
    """실시간 시세 조회 (여러 마켓 한 번에)"""
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


def clear_markets_cache() -> None:
    """마켓 캐시 수동 초기화 (동기화 버튼용)"""
    cache.delete(MARKETS_CACHE_KEY)