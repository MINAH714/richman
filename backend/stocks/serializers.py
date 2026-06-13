# stocks/serializers.py
from rest_framework import serializers
from .models import Watchlist, Portfolio


class PortfolioSerializer(serializers.ModelSerializer):
    """
    포트폴리오 직렬화기
    - 보유 수량, 평균 매입가를 JSON으로 변환
    - 수익률은 DB에 저장하지 않고 여기서 계산해서 내려줌
    """
    # 읽기 전용 필드: DB에 저장하지 않고 계산해서 응답에만 포함
    profit_rate = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = ['id', 'quantity', 'average_price', 'profit_rate', 'updated_at']

    def get_profit_rate(self, obj):
        """
        수익률(%) 계산 메서드
        - current_price는 View에서 context로 넘겨줌
        - 공식: (현재가 - 평균매입가) / 평균매입가 × 100
        """
        current_price = self.context.get('current_price')
        if current_price and obj.average_price:
            rate = (float(current_price) - float(obj.average_price)) / float(obj.average_price) * 100
            return round(rate, 2)   # 소수점 2자리로 반올림
        return None


class WatchlistSerializer(serializers.ModelSerializer):
    """
    관심 종목 직렬화기
    - Watchlist 정보 + 포트폴리오 정보를 한 번에 응답
    - portfolio는 없을 수도 있으므로 required=False
    """
    # 중첩 직렬화: Watchlist 안에 Portfolio 정보도 함께 포함
    portfolio = PortfolioSerializer(read_only=True, required=False)

    class Meta:
        model = Watchlist
        # user는 요청한 사람으로 자동 설정하므로 응답에서는 제외 가능하지만
        # 확인용으로 포함해 둠
        fields = ['id', 'symbol', 'name', 'market', 'added_at', 'portfolio']
        read_only_fields = ['added_at']