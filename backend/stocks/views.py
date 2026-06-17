import math
import requests
from datetime import date, timedelta

import yfinance as yf
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Watchlist, Portfolio, PredictionHistory
from .serializers import (
    WatchlistSerializer,
    PortfolioSerializer,
    PredictionHistorySerializer,
)


def get_current_price(symbol):
    """
    yfinance를 이용해 현재 주가를 가져오는 헬퍼 함수
    - 실패 시 None 반환 (앱이 죽지 않도록 예외 처리 포함)
    """
    try:
        ticker = yf.Ticker(symbol)
        # fast_info는 전체 히스토리 없이 현재가만 빠르게 가져옴
        price = ticker.fast_info.get('lastPrice') or ticker.fast_info.get('last_price')
        return float(price) if price else None
    except Exception:
        return None


# ────────────────────────────────────────────
# 관심 종목 목록 조회 & 추가
# ────────────────────────────────────────────
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])   # 로그인한 사용자만 접근 가능
def watchlist_list(request):
    """
    GET  /api/stocks/watchlist/  → 내 관심 종목 전체 조회
    POST /api/stocks/watchlist/  → 관심 종목 추가
    """
    if request.method == 'GET':
        # 현재 로그인한 유저의 관심 종목만 가져옴
        items = Watchlist.objects.filter(user=request.user)
        result = []

        for item in items:
            # 종목마다 현재가를 yfinance로 조회
            current_price = get_current_price(item.symbol)
            # 수익률 계산을 위해 current_price를 context로 전달
            serializer = WatchlistSerializer(
                item,
                context={'current_price': current_price}
            )
            data = serializer.data
            data['current_price'] = current_price  # 현재가도 함께 응답
            result.append(data)

        return Response(result)

    elif request.method == 'POST':
        # 요청 바디에서 symbol, name, market을 받아 저장
        serializer = WatchlistSerializer(data=request.data)
        if serializer.is_valid():
            # user는 요청한 사람으로 자동 설정
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ────────────────────────────────────────────
# 관심 종목 단건 삭제
# ────────────────────────────────────────────
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def watchlist_detail(request, pk):
    """
    DELETE /api/stocks/watchlist/<pk>/  → 관심 종목 삭제
    """
    try:
        # 본인 것만 삭제 가능 (다른 유저의 것을 삭제 못하게 user 조건 추가)
        item = Watchlist.objects.get(pk=pk, user=request.user)
    except Watchlist.DoesNotExist:
        return Response(
            {'error': '해당 관심 종목을 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )

    item.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ────────────────────────────────────────────
# 포트폴리오 생성 & 수정
# ────────────────────────────────────────────
@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def portfolio_upsert(request, watchlist_id):
    """
    POST /api/stocks/watchlist/<watchlist_id>/portfolio/  → 포트폴리오 등록
    PUT  /api/stocks/watchlist/<watchlist_id>/portfolio/  → 포트폴리오 수정

    upsert = update + insert (있으면 수정, 없으면 생성)
    """
    try:
        # 해당 watchlist가 본인 것인지 확인
        watchlist = Watchlist.objects.get(pk=watchlist_id, user=request.user)
    except Watchlist.DoesNotExist:
        return Response(
            {'error': '관심 종목을 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # 이미 포트폴리오가 있으면 수정, 없으면 새로 생성
    try:
        portfolio = Portfolio.objects.get(watchlist=watchlist)
        serializer = PortfolioSerializer(portfolio, data=request.data)
    except Portfolio.DoesNotExist:
        serializer = PortfolioSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(watchlist=watchlist)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ────────────────────────────────────────────
# 현재가 단건 조회 (즐겨찾기 추가 전 미리 확인용)
# ────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_price(request, symbol):
    """
    GET /api/stocks/price/<symbol>/  → 현재가 조회
    예: GET /api/stocks/price/AAPL/
    """
    price = get_current_price(symbol)
    if price is None:
        return Response(
            {'error': f'{symbol} 종목의 현재가를 가져올 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )
    return Response({'symbol': symbol, 'current_price': price})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_chart(request, symbol):
    """
    GET /api/stocks/chart/<symbol>/
    
    yfinance로 주가 히스토리를 가져와서
    이동평균선(MA)과 볼린저 밴드를 계산해서 내려주는 API
    
    쿼리 파라미터:
    - period: 조회 기간 (기본값 3mo) → 1mo, 3mo, 6mo, 1y
    
    예: GET /api/stocks/chart/AAPL/?period=3mo
    """
    # 쿼리 파라미터에서 기간을 받음, 없으면 3개월(3mo) 기본값
    period = request.query_params.get('period', '3mo')

    try:
        ticker = yf.Ticker(symbol)
        # yfinance로 주가 히스토리 조회
        # interval='1d' → 일봉 기준
        df = ticker.history(period=period, interval='1d')

        if df.empty:
            return Response(
                {'error': f'{symbol} 데이터를 찾을 수 없습니다.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # ── 이동평균선(MA) 계산 ─────────────────────────
        # rolling(n).mean() = 최근 n일의 평균을 구하는 함수
        # 예: MA5 = 최근 5일 종가의 평균
        df['MA5']  = df['Close'].rolling(window=5).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA60'] = df['Close'].rolling(window=60).mean()

        # ── 볼린저 밴드(Bollinger Band) 계산 ────────────
        # 볼린저 밴드 = 이동평균 ± (표준편차 × 2)
        # 상단 밴드: 주가가 여기 위로 올라가면 "과매수" 신호
        # 하단 밴드: 주가가 여기 아래로 내려가면 "과매도" 신호
        df['BB_mid']   = df['Close'].rolling(window=20).mean()
        df['BB_std']   = df['Close'].rolling(window=20).std()
        df['BB_upper'] = df['BB_mid'] + (df['BB_std'] * 2)
        df['BB_lower'] = df['BB_mid'] - (df['BB_std'] * 2)

        # ── 날짜 인덱스를 문자열로 변환 ─────────────────
        # JSON으로 내려보낼 때 datetime 타입은 직렬화가 안 되므로 문자열로 변환
        df.index = df.index.strftime('%Y-%m-%d')

        # ── NaN(계산 불가 값)을 None으로 변환 ───────────
        # rolling 계산 초반부는 데이터가 부족해 NaN이 생김
        # 예: MA60은 처음 60일 이전 데이터는 NaN
        # JSON에서 NaN은 오류이므로 None(null)으로 변환
        def to_val(v):
            import math
            return None if (v is None or (isinstance(v, float) and math.isnan(v))) else round(float(v), 4)

        # ── 응답 데이터 조립 ─────────────────────────────
        result = {
            'symbol': symbol,
            'period': period,
            'dates':  df.index.tolist(),  # x축 날짜 목록
            'candle': [                   # 캔들스틱용 OHLC 데이터
                {
                    'x': date,
                    'y': [
                        to_val(row['Open']),   # 시가
                        to_val(row['High']),   # 고가
                        to_val(row['Low']),    # 저가
                        to_val(row['Close']),  # 종가
                    ]
                }
                for date, row in df.iterrows()
            ],
            'ma': {                       # 이동평균선 데이터
                'ma5':  [to_val(v) for v in df['MA5']],
                'ma20': [to_val(v) for v in df['MA20']],
                'ma60': [to_val(v) for v in df['MA60']],
            },
            'bollinger': {                # 볼린저 밴드 데이터
                'upper': [to_val(v) for v in df['BB_upper']],
                'mid':   [to_val(v) for v in df['BB_mid']],
                'lower': [to_val(v) for v in df['BB_lower']],
            },
            'volume': [to_val(v) for v in df['Volume']],  # 거래량
        }

        return Response(result)

    except Exception as e:
        return Response(
            {'error': f'차트 데이터 조회 중 오류가 발생했습니다: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_search(request):
    """
    GET /api/stocks/search/?q=검색어
    
    yfinance로 종목을 검색해서 자동완성 목록을 반환하는 API
    
    예: GET /api/stocks/search/?q=apple
        GET /api/stocks/search/?q=삼성
    """
    query = request.query_params.get('q', '').strip()

    # 2글자 미만이면 검색하지 않음 (너무 많은 결과 방지)
    if len(query) < 2:
        return Response([])

    try:
        # yfinance의 Search 클래스로 종목 검색
        # max_results: 최대 몇 개까지 반환할지
        search = yf.Search(query, max_results=8)
        quotes = search.quotes  # 검색 결과 목록

        if not quotes:
            return Response([])

        result = []
        for q in quotes:
            # quoteType이 없는 항목은 건너뜀
            if not q.get('quoteType'):
                continue

            result.append({
                'symbol':     q.get('symbol', ''),           # 티커 (예: AAPL)
                'name':       q.get('longname')              # 정식 종목명
                              or q.get('shortname', ''),     # 없으면 약식 종목명
                'market':     q.get('exchDisp', ''),         # 거래소 (예: NASDAQ)
                'type':       q.get('quoteType', ''),        # 종류 (EQUITY, ETF 등)
                'exchange':   q.get('exchange', ''),         # 거래소 코드 (예: NMS)
            })

        return Response(result)

    except Exception as e:
        return Response(
            {'error': f'검색 중 오류가 발생했습니다: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

def get_ai_comment(symbol, name, current_price, predicted_price):
    """
    SSAFY OpenAI API를 호출해서 예측 결과에 대한 짧은 코멘트를 생성하는 헬퍼 함수
    - 실패해도 앱이 죽지 않도록 예외 처리 포함
    """
    try:
        trend = "상승" if predicted_price > current_price else "하락"
        change_pct = abs((predicted_price - current_price) / current_price * 100)

        prompt = (
            f"{name}({symbol}) 종목의 현재가는 {current_price:.2f}이고, "
            f"이동평균 기반 다음 거래일 예측가는 {predicted_price:.2f}입니다 "
            f"({trend} 예상, 변동률 {change_pct:.2f}%). "
            f"이 예측 결과에 대해 투자자에게 도움이 될 만한 짧은 코멘트를 "
            f"2~3문장으로 한국어로 작성해주세요. "
            f"반드시 '이 예측은 참고용이며 투자 손실에 대한 책임을 지지 않습니다'라는 "
            f"문구를 마지막에 포함해주세요."
        )

        # SSAFY OpenAI API 호출
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 200,
        }
        response = requests.post(
            f"{settings.OPENAI_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=10,
        )
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    except Exception:
        # API 실패 시 기본 문구 반환
        return "이 예측은 참고용이며 투자 손실에 대한 책임을 지지 않습니다."


def calculate_predicted_price(symbol):
    """
    이동평균(MA5, MA20) 기반으로 다음 거래일 예측가를 계산하는 헬퍼 함수

    예측 공식:
    - MA5 (단기 추세)와 MA20 (중기 추세)를 가중 평균
    - 단기 추세에 더 가중치를 줌 (MA5 × 0.6 + MA20 × 0.4)
    """
    try:
        ticker = yf.Ticker(symbol)
        # 최근 30일 데이터면 MA20 계산에 충분
        df = ticker.history(period='1mo', interval='1d')

        if len(df) < 5:
            return None, None

        close_prices = df['Close']
        current_price = float(close_prices.iloc[-1])   # 가장 최근 종가

        ma5  = float(close_prices.tail(5).mean())      # 최근 5일 평균
        ma20 = float(close_prices.tail(20).mean()) if len(close_prices) >= 20 else ma5

        # 가중 평균으로 예측가 계산
        predicted_price = ma5 * 0.6 + ma20 * 0.4

        return current_price, round(predicted_price, 4)

    except Exception:
        return None, None


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict_stock(request, symbol):
    """
    POST /api/stocks/predict/<symbol>/

    특정 종목의 다음 거래일 주가를 예측하고 DB에 저장하는 API
    - 이동평균 기반 예측가 계산
    - SSAFY OpenAI API로 AI 코멘트 생성
    - 예측 결과를 PredictionHistory에 저장
    """
    name = request.data.get('name', symbol)   # 종목명 (없으면 티커로 대체)

    # 예측가 계산
    current_price, predicted_price = calculate_predicted_price(symbol)
    if predicted_price is None:
        return Response(
            {'error': f'{symbol} 예측 데이터를 가져올 수 없습니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 다음 거래일 계산 (주말 건너뜀)
    tomorrow = date.today() + timedelta(days=1)
    if tomorrow.weekday() == 5:    # 토요일이면 월요일로
        tomorrow += timedelta(days=2)
    elif tomorrow.weekday() == 6:  # 일요일이면 월요일로
        tomorrow += timedelta(days=1)

    # 이미 오늘 같은 종목을 예측했는지 확인 (중복 방지)
    existing = PredictionHistory.objects.filter(
        user=request.user,
        symbol=symbol,
        predicted_date=tomorrow,
    ).first()

    if existing:
        # 이미 있으면 기존 예측 결과 반환
        serializer = PredictionHistorySerializer(existing)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # AI 코멘트 생성
    ai_comment = get_ai_comment(symbol, name, current_price, predicted_price)

    # DB에 저장
    prediction = PredictionHistory.objects.create(
        user=request.user,
        symbol=symbol,
        name=name,
        predicted_date=tomorrow,
        predicted_price=predicted_price,
        ai_comment=ai_comment,
    )

    serializer = PredictionHistorySerializer(prediction)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def prediction_history(request):
    """
    GET /api/stocks/predictions/

    현재 로그인한 유저의 예측 히스토리 전체 조회
    - actual_price가 없는 항목은 yfinance로 실제 종가를 자동으로 채워줌
    """
    predictions = PredictionHistory.objects.filter(user=request.user)

    # 예측일이 지났는데 actual_price가 없는 항목 → 실제 종가 자동 업데이트
    for pred in predictions:
        if pred.actual_price is None and pred.predicted_date <= date.today():
            try:
                ticker = yf.Ticker(pred.symbol)
                # 예측 대상 날짜 기준 ±2일 범위로 데이터 조회
                hist = ticker.history(
                    start=pred.predicted_date - timedelta(days=2),
                    end=pred.predicted_date + timedelta(days=2),
                )
                if not hist.empty:
                    # 예측일 당일 또는 가장 가까운 날 종가를 실제가로 저장
                    actual = float(hist['Close'].iloc[-1])
                    pred.actual_price = actual
                    pred.save()
            except Exception:
                pass    # 실패해도 조용히 넘어감

    serializer = PredictionHistorySerializer(predictions, many=True)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def prediction_delete(request, pk):
    """
    DELETE /api/stocks/predictions/<pk>/

    예측 히스토리 단건 삭제
    """
    try:
        prediction = PredictionHistory.objects.get(pk=pk, user=request.user)
    except PredictionHistory.DoesNotExist:
        return Response(
            {'error': '예측 기록을 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )
    prediction.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)