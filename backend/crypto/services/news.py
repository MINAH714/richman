# backend/crypto/services/news.py
import re
import requests
from django.conf import settings

NAVER_NEWS_URL = "https://openapi.naver.com/v1/search/news.json"


def _naver_headers() -> dict:
    return {
        "X-Naver-Client-Id": settings.NAVER_NEWS_CLIENT_ID,
        "X-Naver-Client-Secret": settings.NAVER_NEWS_CLIENT_SECRET,
    }


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def fetch_news_count(keyword: str) -> int:
    """키워드로 네이버 뉴스 기사 수 조회"""
    params = {"query": keyword, "display": 100, "sort": "date"}
    try:
        res = requests.get(NAVER_NEWS_URL, headers=_naver_headers(), params=params, timeout=5)
        res.raise_for_status()
        return res.json().get("total", 0)
    except Exception as e:
        print(f"[news] {keyword} 뉴스 조회 실패: {e}")
        return 0


def fetch_news_items(keyword: str, count: int = 5) -> list[dict]:
    """
    키워드 최신 뉴스 목록 조회 (감성 분석용)
    HTML 태그 제거 후 반환: { title, description, link, pubDate }
    """
    params = {"query": keyword, "display": count, "sort": "date"}
    try:
        res = requests.get(NAVER_NEWS_URL, headers=_naver_headers(), params=params, timeout=5)
        res.raise_for_status()
        items = res.json().get("items", [])
        return [
            {
                "title":       _strip_html(item.get("title", "")),
                "description": _strip_html(item.get("description", "")),
                "link":        item.get("originallink") or item.get("link", ""),
                "pubDate":     item.get("pubDate", ""),
            }
            for item in items
        ]
    except Exception as e:
        print(f"[news] {keyword} 뉴스 목록 조회 실패: {e}")
        return []


def calculate_buzz_score(news_count: int, volume_24h: float, prev_volume_24h: float) -> dict:
    """
    Buzz 점수 계산
    - 뉴스 빈도 점수: 최대 70점
    - 거래량 급등 보너스: 전일 대비 200% 이상 시 +30점
    """
    news_score = min(70, (news_count / 1000) * 70)
    volume_bonus = 0
    is_volume_surge = False

    if prev_volume_24h and prev_volume_24h > 0:
        volume_ratio = volume_24h / prev_volume_24h
        if volume_ratio >= 2.0:
            volume_bonus = 30
            is_volume_surge = True

    return {
        "buzz_score":      round(news_score + volume_bonus, 1),
        "news_score":      round(news_score, 1),
        "volume_bonus":    volume_bonus,
        "is_volume_surge": is_volume_surge,
        "news_count":      news_count,
    }