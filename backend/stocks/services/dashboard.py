import re

import yfinance as yf
from django.conf import settings

from .kiwoom import KiwoomApiError, KiwoomConfigError, KiwoomRestClient, kiwoom_dashboard_body


DEFAULT_KIWOOM_DASHBOARD_BODY = {
    "mrkt_tp": "000",
    "sort_tp": "1",
    "trde_qty_cnd": "0000",
    "stk_cnd": "0",
    "crd_cnd": "0",
    "updown_incls": "1",
    "pric_cnd": "0",
    "trde_prica_cnd": "0",
    "stex_tp": "3",
}


KOREAN_DASHBOARD_SEED_STOCKS = [
    {"symbol": "005930.KS", "name": "삼성전자", "market": "KRX"},
    {"symbol": "000660.KS", "name": "SK하이닉스", "market": "KRX"},
    {"symbol": "373220.KS", "name": "LG에너지솔루션", "market": "KRX"},
    {"symbol": "207940.KS", "name": "삼성바이오로직스", "market": "KRX"},
    {"symbol": "005380.KS", "name": "현대차", "market": "KRX"},
    {"symbol": "000270.KS", "name": "기아", "market": "KRX"},
    {"symbol": "068270.KS", "name": "셀트리온", "market": "KRX"},
    {"symbol": "005935.KS", "name": "삼성전자우", "market": "KRX"},
    {"symbol": "035420.KS", "name": "NAVER", "market": "KRX"},
    {"symbol": "105560.KS", "name": "KB금융", "market": "KRX"},
    {"symbol": "051910.KS", "name": "LG화학", "market": "KRX"},
    {"symbol": "012330.KS", "name": "현대모비스", "market": "KRX"},
    {"symbol": "055550.KS", "name": "신한지주", "market": "KRX"},
    {"symbol": "035720.KS", "name": "카카오", "market": "KRX"},
    {"symbol": "028260.KS", "name": "삼성물산", "market": "KRX"},
    {"symbol": "032830.KS", "name": "삼성생명", "market": "KRX"},
    {"symbol": "086790.KS", "name": "하나금융지주", "market": "KRX"},
    {"symbol": "006400.KS", "name": "삼성SDI", "market": "KRX"},
    {"symbol": "033780.KS", "name": "KT&G", "market": "KRX"},
    {"symbol": "003550.KS", "name": "LG", "market": "KRX"},
    {"symbol": "066570.KS", "name": "LG전자", "market": "KRX"},
    {"symbol": "096770.KS", "name": "SK이노베이션", "market": "KRX"},
    {"symbol": "034730.KS", "name": "SK", "market": "KRX"},
    {"symbol": "017670.KS", "name": "SK텔레콤", "market": "KRX"},
    {"symbol": "009150.KS", "name": "삼성전기", "market": "KRX"},
    {"symbol": "018260.KS", "name": "삼성에스디에스", "market": "KRX"},
    {"symbol": "003670.KS", "name": "포스코퓨처엠", "market": "KRX"},
    {"symbol": "010130.KS", "name": "고려아연", "market": "KRX"},
    {"symbol": "011200.KS", "name": "HMM", "market": "KRX"},
    {"symbol": "030200.KS", "name": "KT", "market": "KRX"},
    {"symbol": "024110.KS", "name": "기업은행", "market": "KRX"},
    {"symbol": "000810.KS", "name": "삼성화재", "market": "KRX"},
    {"symbol": "316140.KS", "name": "우리금융지주", "market": "KRX"},
    {"symbol": "034020.KS", "name": "두산에너빌리티", "market": "KRX"},
    {"symbol": "402340.KS", "name": "SK스퀘어", "market": "KRX"},
    {"symbol": "086280.KS", "name": "현대글로비스", "market": "KRX"},
    {"symbol": "009540.KS", "name": "HD한국조선해양", "market": "KRX"},
    {"symbol": "042660.KS", "name": "한화오션", "market": "KRX"},
    {"symbol": "010140.KS", "name": "삼성중공업", "market": "KRX"},
    {"symbol": "267260.KS", "name": "HD현대일렉트릭", "market": "KRX"},
    {"symbol": "138040.KS", "name": "메리츠금융지주", "market": "KRX"},
    {"symbol": "047050.KS", "name": "포스코인터내셔널", "market": "KRX"},
    {"symbol": "005490.KS", "name": "POSCO홀딩스", "market": "KRX"},
    {"symbol": "010950.KS", "name": "S-Oil", "market": "KRX"},
    {"symbol": "090430.KS", "name": "아모레퍼시픽", "market": "KRX"},
    {"symbol": "251270.KS", "name": "넷마블", "market": "KRX"},
    {"symbol": "011070.KS", "name": "LG이노텍", "market": "KRX"},
    {"symbol": "326030.KS", "name": "SK바이오팜", "market": "KRX"},
    {"symbol": "352820.KS", "name": "하이브", "market": "KRX"},
    {"symbol": "377300.KS", "name": "카카오페이", "market": "KRX"},
    {"symbol": "323410.KS", "name": "카카오뱅크", "market": "KRX"},
    {"symbol": "259960.KQ", "name": "크래프톤", "market": "KOSDAQ"},
    {"symbol": "036570.KS", "name": "엔씨소프트", "market": "KRX"},
    {"symbol": "302440.KS", "name": "SK바이오사이언스", "market": "KRX"},
    {"symbol": "009830.KS", "name": "한화솔루션", "market": "KRX"},
    {"symbol": "009420.KS", "name": "한올바이오파마", "market": "KRX"},
    {"symbol": "088350.KS", "name": "한화생명", "market": "KRX"},
    {"symbol": "161390.KS", "name": "한국타이어앤테크놀로지", "market": "KRX"},
    {"symbol": "011780.KS", "name": "금호석유", "market": "KRX"},
    {"symbol": "071050.KS", "name": "한국금융지주", "market": "KRX"},
    {"symbol": "000720.KS", "name": "현대건설", "market": "KRX"},
    {"symbol": "006800.KS", "name": "미래에셋증권", "market": "KRX"},
    {"symbol": "128940.KS", "name": "한미약품", "market": "KRX"},
    {"symbol": "241560.KS", "name": "두산밥캣", "market": "KRX"},
    {"symbol": "028050.KS", "name": "삼성엔지니어링", "market": "KRX"},
    {"symbol": "272210.KS", "name": "한화시스템", "market": "KRX"},
    {"symbol": "005830.KS", "name": "DB손해보험", "market": "KRX"},
    {"symbol": "180640.KS", "name": "한진칼", "market": "KRX"},
    {"symbol": "097950.KS", "name": "CJ제일제당", "market": "KRX"},
    {"symbol": "029780.KS", "name": "삼성카드", "market": "KRX"},
    {"symbol": "021240.KS", "name": "코웨이", "market": "KRX"},
    {"symbol": "271560.KS", "name": "오리온", "market": "KRX"},
    {"symbol": "078930.KS", "name": "GS", "market": "KRX"},
    {"symbol": "004020.KS", "name": "현대제철", "market": "KRX"},
    {"symbol": "008770.KS", "name": "호텔신라", "market": "KRX"},
    {"symbol": "004990.KS", "name": "롯데지주", "market": "KRX"},
    {"symbol": "000100.KS", "name": "유한양행", "market": "KRX"},
    {"symbol": "139480.KS", "name": "이마트", "market": "KRX"},
    {"symbol": "011790.KS", "name": "SKC", "market": "KRX"},
    {"symbol": "047810.KS", "name": "한국항공우주", "market": "KRX"},
    {"symbol": "000120.KS", "name": "CJ대한통운", "market": "KRX"},
    {"symbol": "042700.KS", "name": "한미반도체", "market": "KRX"},
    {"symbol": "000880.KS", "name": "한화", "market": "KRX"},
    {"symbol": "001040.KS", "name": "CJ", "market": "KRX"},
    {"symbol": "014680.KS", "name": "한솔케미칼", "market": "KRX"},
    {"symbol": "120110.KS", "name": "코오롱인더", "market": "KRX"},
    {"symbol": "004170.KS", "name": "신세계", "market": "KRX"},
    {"symbol": "005940.KS", "name": "NH투자증권", "market": "KRX"},
    {"symbol": "267250.KS", "name": "HD현대", "market": "KRX"},
    {"symbol": "005070.KS", "name": "코스모신소재", "market": "KRX"},
    {"symbol": "196170.KQ", "name": "알테오젠", "market": "KOSDAQ"},
    {"symbol": "247540.KQ", "name": "에코프로비엠", "market": "KOSDAQ"},
    {"symbol": "086520.KQ", "name": "에코프로", "market": "KOSDAQ"},
    {"symbol": "091990.KQ", "name": "셀트리온헬스케어", "market": "KOSDAQ"},
    {"symbol": "028300.KQ", "name": "HLB", "market": "KOSDAQ"},
    {"symbol": "035900.KQ", "name": "JYP Ent.", "market": "KOSDAQ"},
    {"symbol": "068760.KQ", "name": "셀트리온제약", "market": "KOSDAQ"},
    {"symbol": "277810.KQ", "name": "레인보우로보틱스", "market": "KOSDAQ"},
    {"symbol": "293490.KQ", "name": "카카오게임즈", "market": "KOSDAQ"},
    {"symbol": "112040.KQ", "name": "위메이드", "market": "KOSDAQ"},
    {"symbol": "058470.KQ", "name": "리노공업", "market": "KOSDAQ"},
    {"symbol": "145020.KQ", "name": "휴젤", "market": "KOSDAQ"},
]


def _to_float(value, absolute=False):
    if value in (None, ""):
        return None

    cleaned = re.sub(r"[^0-9.+-]", "", str(value))
    if cleaned in ("", "+", "-"):
        return None

    try:
        number = float(cleaned)
    except ValueError:
        return None

    return abs(number) if absolute else number


def _change_type(change_rate):
    if change_rate is None:
        return "EVEN"
    if change_rate > 0:
        return "RISE"
    if change_rate < 0:
        return "FALL"
    return "EVEN"


def _normalize_kr_symbol(raw_symbol, market="KRX"):
    digits = re.sub(r"\D", "", str(raw_symbol or ""))
    if len(digits) != 6:
        return str(raw_symbol or "")
    suffix = ".KQ" if market == "KOSDAQ" else ".KS"
    return f"{digits}{suffix}"


def _extract_list(data):
    if isinstance(data, list):
        return data

    preferred_keys = (
        "output",
        "list",
        "items",
        "stk_rank",
        "stk_rank_list",
        "flu_rt_upper",
        "trde_prica_upper",
        "trde_qty_upper",
        "data",
    )
    for key in preferred_keys:
        value = data.get(key) if isinstance(data, dict) else None
        if isinstance(value, list):
            return value

    if isinstance(data, dict):
        for value in data.values():
            if isinstance(value, list) and all(isinstance(item, dict) for item in value):
                return value

    return []


def _market_from_kiwoom_item(item):
    market_text = str(
        item.get("mrkt_nm")
        or item.get("market")
        or item.get("stk_cls")
        or item.get("stex_tp")
        or ""
    ).upper()
    if "KOSDAQ" in market_text or "KQ" in market_text or market_text == "2":
        return "KOSDAQ"
    return "KRX"


def _normalize_kiwoom_item(item, rank):
    market = _market_from_kiwoom_item(item)
    raw_symbol = (
        item.get("stk_cd")
        or item.get("code")
        or item.get("symbol")
        or item.get("isu_cd")
    )
    symbol = _normalize_kr_symbol(raw_symbol, market)
    name = (
        item.get("stk_nm")
        or item.get("name")
        or item.get("isu_nm")
        or item.get("hts_kor_isnm")
        or symbol
    )
    current_price = _to_float(
        item.get("cur_prc")
        or item.get("now_prc")
        or item.get("trade_price")
        or item.get("prpr"),
        absolute=True,
    )
    change_rate = _to_float(
        item.get("flu_rt")
        or item.get("change_rate")
        or item.get("prdy_ctrt")
        or item.get("rate")
    )

    return {
        "rank": rank,
        "symbol": symbol,
        "code": re.sub(r"\D", "", str(raw_symbol or "")),
        "name": str(name).strip(),
        "market": market,
        "current_price": round(current_price, 2) if current_price is not None else None,
        "change_rate": round(change_rate, 2) if change_rate is not None else None,
        "change_type": _change_type(change_rate),
        "trade_volume": _to_float(item.get("trde_qty") or item.get("acml_vol")),
        "trade_value": _to_float(item.get("trde_prica") or item.get("acml_tr_pbmn")),
        "source": "kiwoom",
    }


def _header_value(headers, name):
    for key, value in headers.items():
        if key.lower() == name.lower():
            return value
    return None


def get_korean_stocks_from_kiwoom(offset=0, count=50):
    client = KiwoomRestClient()
    api_id = settings.KIWOOM_DASHBOARD_API_ID
    endpoint = settings.KIWOOM_DASHBOARD_ENDPOINT
    body = kiwoom_dashboard_body() or DEFAULT_KIWOOM_DASHBOARD_BODY

    needed = offset + count
    rows = []
    cont_yn = "N"
    next_key = ""

    while len(rows) < needed:
        data, headers = client.post(endpoint, api_id, body, cont_yn=cont_yn, next_key=next_key)
        page_items = _extract_list(data)
        if not page_items:
            break

        for item in page_items:
            rows.append(_normalize_kiwoom_item(item, len(rows) + 1))

        response_cont = str(_header_value(headers, "cont-yn") or data.get("cont_yn") or "N").upper()
        response_next_key = _header_value(headers, "next-key") or data.get("next_key") or ""
        if response_cont != "Y" or not response_next_key:
            break

        cont_yn = "Y"
        next_key = response_next_key

    return rows[offset:needed], len(rows) >= needed and cont_yn == "Y" and bool(next_key)


def get_korean_stocks_from_yfinance(offset=0, count=50):
    target = KOREAN_DASHBOARD_SEED_STOCKS[offset : offset + count]
    if not target:
        return [], False

    symbols = [item["symbol"] for item in target]
    tickers = yf.Tickers(" ".join(symbols))
    result = []

    for stock in target:
        symbol = stock["symbol"]
        try:
            info = tickers.tickers[symbol].fast_info
            price = info.get("lastPrice") or info.get("last_price")
            prev = info.get("previousClose") or info.get("previous_close")
            current_price = float(price) if price else None
            previous_price = float(prev) if prev else None
            change_rate = None

            if current_price is not None and previous_price not in (None, 0):
                change_rate = (current_price - previous_price) / previous_price * 100

            result.append({
                **stock,
                "rank": offset + len(result) + 1,
                "code": symbol.split(".")[0],
                "current_price": round(current_price, 2) if current_price is not None else None,
                "change_rate": round(change_rate, 2) if change_rate is not None else None,
                "change_type": _change_type(change_rate),
                "source": "yfinance-fallback",
            })
        except Exception:
            result.append({
                **stock,
                "rank": offset + len(result) + 1,
                "code": symbol.split(".")[0],
                "current_price": None,
                "change_rate": None,
                "change_type": "EVEN",
                "source": "yfinance-fallback",
            })

    has_more = (offset + count) < len(KOREAN_DASHBOARD_SEED_STOCKS)
    return result, has_more


def get_korean_dashboard_stocks(offset=0, count=50):
    offset = max(int(offset), 0)
    count = min(max(int(count), 1), settings.STOCK_DASHBOARD_MAX_PAGE_SIZE)

    if KiwoomRestClient.is_configured():
        try:
            stocks, has_more = get_korean_stocks_from_kiwoom(offset, count)
            if stocks:
                return stocks, has_more, "kiwoom"
        except (KiwoomApiError, KiwoomConfigError):
            pass

    stocks, has_more = get_korean_stocks_from_yfinance(offset, count)
    return stocks, has_more, "yfinance-fallback"
