# backend/chatbot/services/chatbot.py
import json
import requests
from openai import OpenAI
from django.conf import settings

# ── 실제 GPT 및 DB 연동을 위해 False로 변경 ──────────────
USE_MOCK = False

client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
)

# 자체 필터링용 금지어 리스트 (Mock 모드용)
BANNED_WORDS = ["시발", "병신", "개새끼", "미친", "존나", "죽어"]


def classify_intent(message: str) -> dict:
    """사용자 메시지의 intent를 분류 및 모더레이션(욕설 필터링) 수행"""
    
    # 1. 모더레이션 체크 (부적절한 언어 차단)
    if USE_MOCK:
        if any(bad_word in message for bad_word in BANNED_WORDS):
            return _moderation_violation_response()
    else:
        try:
            mod_response = client.moderations.create(input=message)
            if mod_response.results[0].flagged:
                return _moderation_violation_response()
        except Exception as e:
            print(f"[chatbot] 모더레이션 체크 실패: {e}")

    # 2. Intent 분류
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
        # 👇 복사 과정에서 끊겼던 바로 그 부분입니다.
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"[chatbot] intent 분류 실패: {e}")
        return {"intent": "mixed", "sub_data": {}, "reason": "분류 실패"}


def _moderation_violation_response() -> dict:
    """모더레이션에 걸렸을 때 반환할 공통 포맷"""
    return {
        "intent": "violation",
        "sub_data": {},
        "reason": "욕설 및 부적절한 언어 감지",
        "answer": "🚨 부적절한 표현이 감지되었습니다. Richman 챗봇은 바르고 고운 말만 이해할 수 있어요!"
    }


def _mock_classify_intent(message: str) -> dict:
    """키워드 기반 임시 intent 분류 (Mock)"""
    msg = message.lower()

    if any(k in msg for k in ["되면 알려", "알림", "목표가"]):
        coin = _extract_coin_symbol(msg)
        price = _extract_price(msg)
        direction = "below" if any(k in msg for k in ["이하", "내려", "떨어"]) else "above"
        return {
            "intent": "price_alert",
            "sub_data": {"coin_symbol": coin, "target_price": price, "direction": direction},
            "reason": "mock: 가격 알림 요청"
        }

    if any(k in msg for k in ["비트코인", "이더리움", "리플", "솔라나", "도지", "btc", "eth", "xrp", "sol", "코인", "크립토", "암호화폐"]):
        coin = _extract_coin_symbol(msg)
        return {"intent": "crypto", "sub_data": {"coin_symbol": coin}, "reason": "mock: 크립토 관련"}

    if any(k in msg for k in ["주식", "삼성", "애플", "종목", "코스피", "나스닥", "etf", "수익률"]):
        return {"intent": "stock", "sub_data": {"ticker": None}, "reason": "mock: 주식 관련"}

    if any(k in msg for k in ["소비", "지출", "식비", "카페", "정산", "가계부", "얼마", "썼", "달력"]):
        return {"intent": "consumption", "sub_data": {"date": None, "category": None}, "reason": "mock: 소비 관련"}

    if any(k in msg for k in ["예금", "적금", "금리", "은행", "이자", "저축", "상품"]):
        return {"intent": "finlife", "sub_data": {"bank": None}, "reason": "mock: 예적금 관련"}

    return {"intent": "mixed", "sub_data": {}, "reason": "mock: 분류 불가"}


def _extract_coin_symbol(msg: str) -> str | None:
    coin_map = {
        "비트코인": "BTC", "btc": "BTC", "이더리움": "ETH", "eth": "ETH",
        "리플": "XRP", "xrp": "XRP", "솔라나": "SOL", "sol": "SOL", "도지": "DOGE", "doge": "DOGE",
    }
    for keyword, symbol in coin_map.items():
        if keyword in msg: return symbol
    return None


def _extract_price(msg: str) -> float | None:
    import re
    msg = msg.replace(",", "").replace(" ", "")
    match = re.search(r'(\d+(?:\.\d+)?)억', msg)
    if match: return float(match.group(1)) * 100_000_000
    match = re.search(r'(\d+(?:\.\d+)?)천만', msg)
    if match: return float(match.group(1)) * 10_000_000
    match = re.search(r'(\d+(?:\.\d+)?)만', msg)
    if match: return float(match.group(1)) * 10_000
    match = re.search(r'\d+', msg)
    if match: return float(match.group())
    return None


# ── 도메인별 처리 핸들러 ────────────────────────────────────

def handle_crypto_intent(message: str, sub_data: dict) -> dict:
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
                }
        except Exception: pass

        try:
            sentiment = CoinSentiment.objects.filter(coin_symbol=coin_symbol.upper()).order_by("-analyzed_at").first()
            if sentiment:
                context_data["sentiment"] = {
                    "positive": round(sentiment.positive_score * 100, 1),
                    "negative": round(sentiment.negative_score * 100, 1),
                }
        except Exception: pass

    if USE_MOCK:
        answer = "🪙 크립토 기능입니다. 코인 시세와 AI 감성 분석 결과를 제공해 드려요." if not coin_symbol else f"📊 {coin_symbol}의 시세를 불러왔습니다."
        return {"answer": answer, "context_data": context_data, "coin_symbol": coin_symbol}

    system_prompt = f"""너는 Richman의 크립토 어시스턴트야. 실시간 데이터를 참고해 한국어로 답해. 3문장 이내.
실시간 데이터: {json.dumps(context_data, ensure_ascii=False)}"""

    try:
        res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": message}], max_tokens=200)
        return {"answer": res.choices[0].message.content.strip(), "context_data": context_data, "coin_symbol": coin_symbol}
    except Exception: return {"answer": "죄송해요, 코인 정보를 불러오지 못했어요."}


def handle_stock_intent(message: str, sub_data: dict) -> dict:
    context_data = {}
    if USE_MOCK:
        return {"answer": "📈 주식 관련 기능은 준비 중이에요! 관심 종목 시세와 차트를 곧 조회할 수 있어요.", "context_data": context_data}
    
    system_prompt = f"너는 Richman의 주식 어시스턴트야. 객관적 정보만 3문장 이내로 제공해.\n데이터: {json.dumps(context_data)}"
    try:
        res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": message}], max_tokens=200)
        return {"answer": res.choices[0].message.content.strip(), "context_data": context_data}
    except Exception: return {"answer": "죄송해요, 주식 정보를 불러오지 못했어요."}


def handle_consumption_intent(message: str, sub_data: dict) -> dict:
    context_data = {}
    if USE_MOCK:
        return {"answer": "💸 소비 관리 기능은 준비 중이에요! 달력 지출 내역과 통계를 곧 이용할 수 있어요.", "context_data": context_data}
    
    system_prompt = f"너는 Richman의 소비 관리 어시스턴트야. 소비 데이터를 참고해 3문장 이내로 답해.\n데이터: {json.dumps(context_data)}"
    try:
        res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": message}], max_tokens=200)
        return {"answer": res.choices[0].message.content.strip(), "context_data": context_data}
    except Exception: return {"answer": "죄송해요, 소비 정보를 불러오지 못했어요."}


def handle_finlife_intent(message: str, sub_data: dict) -> dict:
    """새로 추가된 finlife(예적금) intent 처리 핸들러"""
    context_data = {}
    if not USE_MOCK:
        try:
            # 상위 예적금 상품 3개 정도를 DB에서 불러와 GPT에게 넘겨줌
            from finlife.models import DepositProduct
            top_products = DepositProduct.objects.all()[:3]
            context_data["recommended_products"] = [
                {"bank": p.kor_co_nm, "name": p.fin_prdt_nm} for p in top_products
            ]
        except Exception:
            pass

    if USE_MOCK:
        return {
            "answer": "🏦 예적금 추천 기능이에요! 고객님의 성향에 맞는 금융감독원 최고 금리 상품을 찾아 드릴게요.",
            "context_data": context_data,
        }

    system_prompt = f"""너는 Richman의 예적금(Finlife) 어시스턴트야.
아래 금융감독원 상품 데이터를 참고해서 친절하고 간결하게 한국어로 답해.
답변은 3~5문장 이내로 작성해.

상품 데이터:
{json.dumps(context_data, ensure_ascii=False, indent=2)}
"""
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            max_tokens=300,
            temperature=0.7,
        )
        return {"answer": res.choices[0].message.content.strip(), "context_data": context_data}
    except Exception as e:
        print(f"[chatbot] finlife 응답 실패: {e}")
        return {"answer": "죄송해요, 은행 상품 정보를 불러오지 못했어요."}


def handle_mixed_intent(message: str) -> dict:
    """모든 도메인(예적금, 주식, 크립토, 소비)을 아우르는 일반/혼합 질문 처리"""
    if USE_MOCK:
        return {
            "answer": "안녕하세요! 저는 Richman 금융 통합 어시스턴트예요 💰\n예적금 추천, 비트코인 시세, 주식 흐름, 소비 내역 등 무엇이든 물어보세요!",
        }

    system_prompt = """너는 Richman의 전천후 금융 통합 어시스턴트야.
예금/적금, 암호화폐, 주식, 소비 관리 등 4가지 도메인 전반에 걸쳐 친절하고 간결하게 한국어로 답해.
투자 권유나 확정적 예측은 절대 피하고, 객관적인 금융 정보만 제공해.
사용자에게 도움이 될만한 인사이트를 3~5문장 이내로 정리해줘."""

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
사용자 질문을 아래 중 하나로 엄격하게 분류해:

- crypto: 암호화폐 시세, 즐겨찾기, Buzz, 감성분석
- stock: 주식 시세, 관심종목, 수익률, 이동평균선
- consumption: 소비 내역, 달력, 가계부, 지출
- finlife: 예금, 적금, 금리, 은행 상품, 저축
- price_alert: "X가 얼마 되면 알려줘" 형태의 알림 설정
- mixed: 두 개 이상의 영역이 섞인 질문이거나 단순 인사말

반드시 아래 JSON 형식으로만 응답해. 마크다운 코드블록 없이 순수 JSON만 반환할 것:
{
  "intent": "crypto",
  "sub_data": {
    "coin_symbol": "BTC",
    "ticker": null,
    "date": null,
    "category": null,
    "target_price": null,
    "direction": null,
    "bank": null
  },
  "reason": "비트코인 가격을 물어봄"
}
"""