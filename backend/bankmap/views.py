# bankmap/views.py
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

class BankSearchView(APIView):
    """
    GET /api/bankmap/search/?province=서울특별시&district=강남구&brand=KB국민은행
    드롭다운으로 선택한 지역 + 은행사명으로 카카오 키워드 검색
    → 결과 중 실제 주소가 선택한 시/군/구를 포함하는 곳만 필터링
    """
    permission_classes = [AllowAny]

    def get(self, request):
        province = request.query_params.get('province')
        district = request.query_params.get('district')
        brand    = request.query_params.get('brand')

        if not all([province, district, brand]):
            return Response(
                {'error': 'province, district, brand 모두 필요합니다.'},
                status=400,
            )

        query = f'{province} {district} {brand}'

        url = 'https://dapi.kakao.com/v2/local/search/keyword.json'
        headers = {'Authorization': f'KakaoAK {settings.KAKAO_REST_API_KEY}'}
        params = {
            'query': query,
            'category_group_code': 'BK9',
            'size': 15,
        }

        res = requests.get(url, headers=headers, params=params)

        if res.status_code != 200:
            return Response(
                {'error': '카카오 API 호출 실패', 'detail': res.text},
                status=res.status_code,
            )

        data = res.json()
        documents = data.get('documents', [])

        banks = []
        for doc in documents:
            address = doc['road_address_name'] or doc['address_name']
            name    = doc['place_name']

            # ① 주소에 시/군/구가 실제로 포함되는지 확인
            district_match = district in address

            # ② 은행명에 선택한 은행사명이 포함되는지 확인 (한 번 더 정확도 보강)
            brand_match = brand in name

            if district_match and brand_match:
                banks.append({
                    'id': doc['id'],
                    'name': name,
                    'address': address,
                    'phone': doc['phone'],
                    'lat': float(doc['y']),
                    'lng': float(doc['x']),
                    'place_url': doc['place_url'],
                })

        return Response({'banks': banks, 'count': len(banks), 'query': query})

class DirectionsView(APIView):
    """
    GET /api/bankmap/directions/?start_x=127.039585&start_y=37.5012743&end_x=...&end_y=...
    카카오 모빌리티 길찾기 (자동차)
    """
    permission_classes = [AllowAny]

    def get(self, request):
        start_x = request.query_params.get('start_x')
        start_y = request.query_params.get('start_y')
        end_x   = request.query_params.get('end_x')
        end_y   = request.query_params.get('end_y')

        if not all([start_x, start_y, end_x, end_y]):
            return Response({'error': '출발지/목적지 좌표가 모두 필요합니다.'}, status=400)

        url = 'https://apis-navi.kakaomobility.com/v1/directions'
        headers = {'Authorization': f'KakaoAK {settings.KAKAO_REST_API_KEY}'}
        params = {
            'origin': f'{start_x},{start_y}',
            'destination': f'{end_x},{end_y}',
            'priority': 'RECOMMEND',
        }

        res = requests.get(url, headers=headers, params=params)

        if res.status_code != 200:
            return Response({
                'error': 'Mobility API 호출 실패 (승인 대기 중일 수 있습니다)',
                'detail': res.text,
            }, status=res.status_code)

        data = res.json()
        try:
            route = data['routes'][0]
            summary = route['summary']

            path = []
            for section in route['sections']:
                for road in section['roads']:
                    vertexes = road['vertexes']
                    for i in range(0, len(vertexes), 2):
                        path.append({'lng': vertexes[i], 'lat': vertexes[i + 1]})

            return Response({
                'distance': summary['distance'],
                'duration': summary['duration'],
                'taxi_fare': summary.get('fare', {}).get('taxi'),
                'toll_fare': summary.get('fare', {}).get('toll'),
                'path': path,
            })
        except (KeyError, IndexError):
            return Response({'error': '경로를 찾을 수 없습니다.', 'raw': data}, status=404)