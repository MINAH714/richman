# backend/chatbot/services/chatbot.py
import json
import requests
from openai import OpenAI
from django.conf import settings

# ── Mock 모드 플래그 (학원에서 False로 변경) ──────────────
USE_MOCK = True

client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
)


def classify_intent(message: str) -> dict:
    """사용자 메시지의 intent를 분류"""
    if USE_MOCK:
        return _mock_classify_intent(message)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            max_tokens=200,
            temperature=0,
        )
        content = response.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"[chatbot] intent 분류 실패: {e}")
        return {"intent": "mixed", "sub_data": {}, "reason": "분류 실패"}


def _mock_classify_intent(message: str) -> dict:
    """키워드 기반 임시 intent 분류 (Mock)"""
    msg = message.lower()

    # 가격 알림
    if any(k in msg for k in ["되면 알려", "알림", "목표가"]):
        coin = _extract_coin_symbol(msg)
        price = _extract_price(msg)
        direction = "below" if any(k in msg for k in ["이하", "내려", "떨어"]) else "above"
        return {
            "intent": "price_alert",
            "sub_data": {
                "coin_symbol": coin,
                "target_price": price,
                "direction": direction,
            },
            "reason": "mock: 가격 알림 요청"
        }

    # 크립토
    if any(k in msg for k in ["비트코인", "이더리움", "리플", "솔라나", "도지", "btc", "eth", "xrp", "sol", "코인", "크립토", "암호화폐"]):
        coin = _extract_coin_symbol(msg)
        return {
            "intent": "crypto",
            "sub_data": {"coin_symbol": coin},
            "reason": "mock: 크립토 관련"
        }

    # 주식
    if any(k in msg for k in ["주식", "삼성", "애플", "종목", "코스피", "나스닥", "etf", "수익률"]):
        return {
            "intent": "stock",
            "sub_data": {"ticker": None},
            "reason": "mock: 주식 관련"
        }

    # 소비
    if any(k in msg for k in ["소비", "지출", "식비", "카페", "정산", "가계부", "얼마", "썼", "달력"]):
        return {
            "intent": "consumption",
            "sub_data": {"date": None, "category": None},
            "reason": "mock: 소비 관련"
        }

    return {"intent": "mixed", "sub_data": {}, "reason": "mock: 분류 불가"}


def _extract_coin_symbol(msg: str) -> str | None:
    """메시지에서 코인 심볼 추출"""
    coin_map = {
        "비트코인": "BTC", "btc": "BTC",
        "이더리움": "ETH", "eth": "ETH",
        "리플": "XRP", "xrp": "XRP",
        "솔라나": "SOL", "sol": "SOL",
        "도지": "DOGE", "doge": "DOGE",
    }
    for keyword, symbol in coin_map.items():
        if keyword in msg:
            return symbol
    return None


def _extract_price(msg: str) -> float | None:
    """메시지에서 목표가 추출"""
    import re
    # "1억", "5천만", "1억5천" 등 한국어 숫자 파싱
    msg = msg.replace(",", "").replace(" ", "")

    # 억 단위
    match = re.search(r'(\d+(?:\.\d+)?)억', msg)
    if match:
        return float(match.group(1)) * 100_000_000

    # 천만 단위
    match = re.search(r'(\d+(?:\.\d+)?)천만', msg)
    if match:
        return float(match.group(1)) * 10_000_000

    # 만 단위
    match = re.search(r'(\d+(?:\.\d+)?)만', msg)
    if match:
        return float(match.group(1)) * 10_000

    # 순수 숫자
    match = re.search(r'\d+', msg)
    if match:
        return float(match.group())

    return None


def handle_crypto_intent(message: str, sub_data: dict) -> dict:
    """crypto intent 처리"""
    from crypto.services.upbit import get_ticker, get_all_krw_markets
    from crypto.models import CoinBuzz, CoinSentiment

    coin_symbol = sub_data.get("coin_symbol")
    context_data = {}

    if coin_symbol:
        market = f"KRW-{coin_symbol.upper()}"

        try:
            ticker = get_ticker([market])
            if ticker:
                t = ticker[0]
                context_data["price"] = {
                    "trade_price": t.get("trade_price"),
                    "change_rate": round((t.get("change_rate") or 0) * 100, 2),
                    "change": t.get("change"),
                    "high_price": t.get("high_price"),
                    "low_price": t.get("low_price"),
                }
        except Exception:
            pass

        try:
            markets = get_all_krw_markets()
            meta = next((m for m in markets if m["market"] == market), None)
            if meta:
                context_data["coin_name"] = meta["korean_name"]
        except Exception:
            pass

        try:
            buzz = CoinBuzz.objects.filter(coin_symbol=coin_symbol.upper()).order_by("-measured_at").first()
            if buzz:
                context_data["buzz"] = {
                    "buzz_score": buzz.buzz_score,
                    "news_count": buzz.news_count,
                }
        except Exception:
            pass

        try:
            sentiment = CoinSentiment.objects.filter(coin_symbol=coin_symbol.upper()).order_by("-analyzed_at").first()
            if sentiment:
                context_data["sentiment"] = {
                    "positive": round(sentiment.positive_score * 100, 1),
                    "neutral": round(sentiment.neutral_score * 100, 1),
                    "negative": round(sentiment.negative_score * 100, 1),
                }
        except Exception:
            pass

    if USE_MOCK:
        # Mock 응답 — 실제 데이터는 조회하되 GPT 응답 대신 포맷된 텍스트 반환
        answer = _mock_crypto_answer(coin_symbol, context_data)
        return {"answer": answer, "context_data": context_data, "coin_symbol": coin_symbol}

    system_prompt = f"""너는 Richman의 크립토 어시스턴트야.
아래 실시간 데이터를 참고해서 친절하고 간결하게 한국어로 답해.
숫자는 한국 단위로 표현해 (예: 1억 2345만 원).
답변은 3~5문장 이내로.

실시간 데이터:
{json.dumps(context_data, ensure_ascii=False, indent=2)}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            max_tokens=300,
            temperature=0.7,
        )
        return {
            "answer": response.choices[0].message.content.strip(),
            "context_data": context_data,
            "coin_symbol": coin_symbol,
        }
    except Exception as e:
        print(f"[chatbot] crypto 응답 실패: {e}")
        return {"answer": "죄송해요, 지금은 답변을 생성할 수 없어요."}


def _mock_crypto_answer(coin_symbol: str | None, context_data: dict) -> str:
    """Mock 크립토 응답 생성"""
    if not coin_symbol:
        return "어떤 코인에 대해 알고 싶으신가요? 비트코인, 이더리움, 리플 등을 물어보세요!"

    coin_name = context_data.get("coin_name", coin_symbol)
    price_data = context_data.get("price", {})
    buzz_data = context_data.get("buzz", {})
    sentiment_data = context_data.get("sentiment", {})

    lines = []

    if price_data:
        price = price_data.get("trade_price", 0)
        rate = price_data.get("change_rate", 0)
        direction = "📈" if price_data.get("change") == "RISE" else "📉" if price_data.get("change") == "FALL" else "➡️"

        if price >= 100_000_000:
            price_str = f"{price / 100_000_000:.2f}억 원"
        elif price >= 10_000:
            price_str = f"{price:,.0f}원"
        else:
            price_str = f"{price:.4f}원"

        lines.append(f"{direction} **{coin_name}** 현재가: {price_str} ({rate:+.2f}%)")
    else:
        lines.append(f"📊 {coin_name} 시세를 불러오는 중이에요.")

    if buzz_data:
        score = buzz_data.get("buzz_score", 0)
        news = buzz_data.get("news_count", 0)
        lines.append(f"🔥 Buzz 점수: {score}점 (뉴스 {news:,}건)")

    if sentiment_data:
        pos = sentiment_data.get("positive", 0)
        neg = sentiment_data.get("negative", 0)
        mood = "긍정적" if pos > 50 else "부정적" if neg > 50 else "중립적"
        lines.append(f"😊 시장 감성: {mood} (긍정 {pos}% / 부정 {neg}%)")

    return "\n".join(lines)


def handle_stock_intent(message: str, sub_data: dict) -> dict:
    """stock intent 처리"""
    ticker = sub_data.get("ticker")
    context_data = {}

    if ticker and not USE_MOCK:
        try:
            res = requests.get(
                f"http://127.0.0.1:8000/api/stock/indicators/{ticker}/",
                timeout=5
            )
            if res.status_code == 200:
                data = res.json()
                context_data["indicators"] = {
                    "ma5": data.get("ma5", [None])[-1],
                    "ma20": data.get("ma20", [None])[-1],
                    "ma60": data.get("ma60", [None])[-1],
                }
        except Exception:
            pass

    if USE_MOCK:
        return {
            "answer": "📈 주식 관련 기능은 현재 준비 중이에요! 관심 종목 시세, 이동평균선, 볼린저 밴드 등을 곧 조회할 수 있어요.",
            "context_data": context_data,
        }

    system_prompt = f"""너는 Richman의 주식 어시스턴트야.
아래 데이터를 참고해서 친절하고 간결하게 한국어로 답해.
투자 권유나 확정적 예측은 하지 말고 객관적인 정보만 제공해.
답변은 3~5문장 이내로.

데이터:
{json.dumps(context_data, ensure_ascii=False, indent=2)}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            max_tokens=300,
            temperature=0.7,
        )
        return {
            "answer": response.choices[0].message.content.strip(),
            "context_data": context_data,
        }
    except Exception as e:
        print(f"[chatbot] stock 응답 실패: {e}")
        return {"answer": "죄송해요, 주식 정보를 불러오지 못했어요."}


def handle_consumption_intent(message: str, sub_data: dict) -> dict:
    """consumption intent 처리"""
    context_data = {}

    if not USE_MOCK:
        date = sub_data.get("date")
        try:
            stats_res = requests.get("http://127.0.0.1:8000/api/ledgers/stats/", timeout=5)
            if stats_res.status_code == 200:
                context_data["category_stats"] = stats_res.json()
        except Exception:
            pass

        if date:
            try:
                daily_res = requests.get(f"http://127.0.0.1:8000/api/ledgers/daily/?date={date}", timeout=5)
                if daily_res.status_code == 200:
                    context_data["daily"] = daily_res.json()
            except Exception:
                pass

    if USE_MOCK:
        return {
            "answer": "💸 소비 관리 기능은 현재 준비 중이에요! 달력에서 일별 지출 내역, 카테고리별 통계, 정산 기능 등을 곧 이용할 수 있어요.",
            "context_data": context_data,
        }

    system_prompt = f"""너는 Richman의 소비 관리 어시스턴트야.
아래 소비 데이터를 참고해서 친절하고 간결하게 한국어로 답해.
답변은 3~5문장 이내로.

소비 데이터:
{json.dumps(context_data, ensure_ascii=False, indent=2)}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            max_tokens=300,
            temperature=0.7,
        )
        return {
            "answer": response.choices[0].message.content.strip(),
            "context_data": context_data,
        }
    except Exception as e:
        print(f"[chatbot] consumption 응답 실패: {e}")
        return {"answer": "죄송해요, 소비 정보를 불러오지 못했어요."}


def handle_mixed_intent(message: str) -> dict:
    """mixed intent — 일반 GPT 응답"""
    if USE_MOCK:
        return {
            "answer": "안녕하세요! 저는 Richman 금융 어시스턴트예요 💰\n비트코인 시세, 주식 정보, 소비 내역 등을 물어보세요!",
        }

    system_prompt = """너는 Richman의 금융 어시스턴트야.
암호화폐, 주식, 소비 관리 전반에 걸쳐 친절하고 간결하게 한국어로 답해.
투자 권유나 확정적 예측은 하지 말고 일반적인 금융 정보를 제공해.
답변은 3~5문장 이내로."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            max_tokens=300,
            temperature=0.7,
        )
        return {"answer": response.choices[0].message.content.strip()}
    except Exception as e:
        print(f"[chatbot] mixed 응답 실패: {e}")
        return {"answer": "죄송해요, 지금은 답변을 생성할 수 없어요."}


# ── Intent 분류 프롬프트 (GPT 모드용) ────────────────────
INTENT_SYSTEM_PROMPT = """너는 금융 통합 플랫폼 Richman의 의도 분류기야.
사용자 질문을 아래 중 하나로 분류해:

- crypto: 암호화폐 시세, 즐겨찾기, Buzz, 감성분석, 가격 알림
- stock: 주식 시세, 관심종목, 수익률, 이동평균선, 볼린저밴드
- consumption: 소비 내역, 달력, 정산, 카테고리 지출, 고정지출
- mixed: 두 개 이상 영역이 섞인 질문
- price_alert: "X가 얼마 되면 알려줘" 형태의 가격 알림 설정

반드시 아래 JSON 형식으로만 응답해. 마크다운 코드블록 없이 순수 JSON만:
{
  "intent": "crypto",
  "sub_data": {
    "coin_symbol": "BTC",
    "ticker": null,
    "date": null,
    "category": null,
    "target_price": null,
    "direction": null
  },
  "reason": "비트코인 가격을 물어봄"
}
"""