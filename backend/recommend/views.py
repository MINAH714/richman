# recommend/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.models import UserProfile
from .services import get_recommendations
from .serializers import RecommendedProductSerializer


class RecommendationView(APIView):
    """
    GET /api/recommend/
    로그인한 사용자의 온보딩 설문 데이터를 기반으로
    유사도 점수가 가장 높은 예적금 상품 N개를 추천한다.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return Response({
                'recommendations': [],
                'message': '온보딩 설문을 먼저 완료해주세요.',
            }, status=200)

        if not profile.is_onboarded:
            return Response({
                'recommendations': [],
                'message': '온보딩 설문을 먼저 완료해주세요.',
            }, status=200)

        results = get_recommendations(profile, limit=5)

        # 요구사항 ④ - 추천 결과가 없을 경우 대체 문구 제공
        if not results:
            return Response({
                'recommendations': [],
                'message': '현재 조건에 맞는 추천 상품이 없습니다. 등록된 예적금 상품이 충분하지 않거나, 조건에 맞는 상품을 찾지 못했어요. 잠시 후 다시 시도해주세요.',
            }, status=200)

        serializer = RecommendedProductSerializer(results, many=True)
        return Response({
            'recommendations': serializer.data,
            'message': None,
            'algorithm': 'weighted-similarity',  # 발표용: 사용한 알고리즘 명시
        }, status=200)