# backend/crypto/services/sentiment.py

import json
import re
from openai import OpenAI
from django.conf import settings
from .news import fetch_news_items

client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
)


def analyze_coin_sentiment(coin_symbol: str, coin_name: str = "") -> dict:
    """
    코인별 최신 뉴스 5건 → GPT(gpt-4o-mini) 감성 분석

    Returns:
        {
            positive_score: float (0.0 ~ 1.0),
            neutral_score:  float (0.0 ~ 1.0),
            negative_score: float (0.0 ~ 1.0),
            summary: str,
            articles: list[dict],
            news_count: int,
        }
        ※ positive + neutral + negative 합계 = 1.0 보장
    """
    query = coin_name if coin_name else coin_symbol.replace("KRW-", "")
    articles = fetch_news_items(query, count=5)
    news_count = len(articles)

    if news_count == 0:
        return {
            "positive_score": 0.0,
            "neutral_score": 1.0,
            "negative_score": 0.0,
            "summary": "분석할 뉴스가 없습니다.",
            "articles": [],
            "news_count": 0,
        }

    news_text = "\n".join(
        [
            f"{i + 1}. 제목: {a['title']} / 내용: {a['description']}"
            for i, a in enumerate(articles)
        ]
    )

    prompt = f"""다음은 암호화폐 '{coin_symbol}'({coin_name})에 관한 최신 뉴스 {news_count}건입니다.

{news_text}

위 뉴스들의 전반적인 시장 감성을 분석하세요.
반드시 아래 JSON 형식으로만 응답하고 다른 텍스트는 포함하지 마세요.
세 비율(positive + neutral + negative)의 합계는 반드시 1.0이어야 합니다.

{{
  "positive": <긍정 비율, 소수점 둘째 자리, 예: 0.45>,
  "neutral": <중립 비율, 소수점 둘째 자리, 예: 0.35>,
  "negative": <부정 비율, 소수점 둘째 자리, 예: 0.20>,
  "summary": "<전체 시장 분위기 한 줄 요약, 35자 이내>"
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=200,
        )
        raw = response.choices[0].message.content.strip()
        # 마크다운 코드 펜스 제거
        raw = re.sub(r"```(?:json)?", "", raw).strip()
        data = json.loads(raw)

        positive = round(float(data.get("positive", 0.0)), 2)
        neutral = round(float(data.get("neutral", 0.0)), 2)
        negative = round(float(data.get("negative", 0.0)), 2)
        summary = str(data.get("summary", "분석 완료"))[:50]

        # 합계 1.0 보정 (부동소수 오차 흡수)
        total = round(positive + neutral + negative, 2)
        if total != 1.0:
            diff = round(1.0 - total, 2)
            neutral = round(neutral + diff, 2)

        # 음수 방어
        positive = max(0.0, positive)
        neutral = max(0.0, neutral)
        negative = max(0.0, negative)

        return {
            "positive_score": positive,
            "neutral_score": neutral,
            "negative_score": negative,
            "summary": summary,
            "articles": articles,
            "news_count": news_count,
        }

    except json.JSONDecodeError:
        return {
            "positive_score": 0.0,
            "neutral_score": 1.0,
            "negative_score": 0.0,
            "summary": "GPT 응답 파싱 오류",
            "articles": articles,
            "news_count": news_count,
        }
    except Exception as e:
        return {
            "positive_score": 0.0,
            "neutral_score": 1.0,
            "negative_score": 0.0,
            "summary": f"분석 오류: {str(e)[:30]}",
            "articles": articles,
            "news_count": news_count,
        }