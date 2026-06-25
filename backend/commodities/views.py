# backend/commodities/views.py
import os
import pandas as pd
import datetime
from django.conf import settings
from django.http import JsonResponse

def get_commodity_data(request, asset_type):
    """
    금/은 엑셀 데이터를 정제하여 프론트엔드로 전달하는 API (따옴표 및 헤더 완전 박멸 버전)
    """
    asset_type = asset_type.lower()
    if asset_type not in ['gold', 'silver']:
        return JsonResponse({'error': '올바르지 않은 자산 타입입니다.'}, status=400)

    # 1. 파일 경로 설정
    file_name = 'Gold_prices.xlsx' if asset_type == 'gold' else 'Silver_prices.xlsx'
    file_path = os.path.join(settings.BASE_DIR, 'data', file_name)

    try:
        df = pd.read_excel(file_path, engine='openpyxl')
    except FileNotFoundError:
        return JsonResponse({'error': f'{file_name} 파일이 없습니다.'}, status=404)

    # 🎯 2. [초강력 방어 1] 컬럼 헤더(제목) 자체에 포함된 온갖 따옴표와 공백을 완전히 제거합니다.
    # 예: '"Close/Last"' 또는 ' Close/Last ' -> 'Close/Last'로 강제 정제
    df.columns = df.columns.astype(str).str.replace(r'[\"\s\'“_”‘_’]', '', regex=True)

    # 3. 깨끗해진 헤더를 바탕으로 안전하게 이름 변경 (Close/Last -> Price, Volume -> Vol.)
    df = df.rename(columns={
        'Close/Last': 'Price',
        'Volume': 'Vol.'
    })

    numeric_cols = ['Price', 'Open', 'High', 'Low', 'Vol.']

    # 🎯 4. [초강력 방어 2] 데이터 내부의 모든 따옴표, 쉼표, 공백을 예외 없이 강제로 문자열 치환하여 밀어버립니다.
    # 예: '"1,967.10"' -> '1967.10'으로 완벽 수선
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'[,\"\s\'“_”‘_’]', '', regex=True)

    # 5. 은(Silver) 데이터 전용: 날짜로 오인입된 가격 복원 (Day.month 가설)
    if asset_type == 'silver':
        def fix_date_to_price(val):
            # 위에서 공백이 제거되어 '2024-05-2300:00:00' 같은 형태로 들어옵니다.
            if '-' in val:
                try:
                    # 앞의 10자리(YYYY-MM-DD)만 안전하게 잘라서 파싱 진행
                    dt = pd.to_datetime(val[:10])
                    return float(f"{dt.day}.{dt.month:02d}")
                except Exception:
                    return val
            return val

        for col in ['Open', 'High', 'Low']:
            if col in df.columns:
                df[col] = df[col].apply(fix_date_to_price)

    # 6. 모든 숫자 컬럼을 순수 float 숫자로 최종 형변환 (실패한 빈 값은 NaN 처리)
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
    # 날짜 컬럼도 따옴표 제거 후 포맷 정리
    if 'Date' in df.columns:
        df['Date'] = df['Date'].astype(str).str.replace(r'[\"\s\'“_”‘_’]', '', regex=True)
        df = df[df['Date'] != 'nan']  # 무효 행 제외
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')

    # 날짜 기준 오름차순 정렬
    df = df.sort_values('Date').reset_index(drop=True)
    
    # 7. 누락 컬럼 방어 및 필요한 6개 컬럼만 슬라이싱하여 딕셔너리 리스트 생성
    required_cols = ['Date', 'Price', 'Open', 'High', 'Low', 'Vol.']
    for c in required_cols:
        if c not in df.columns:
            df[c] = None
            
    result_data = df[required_cols].to_dict('records')
    
    # 8. 최종 결측치(NaN)를 None(null)으로 치환하여 장고 500 에러 원천 차단
    for record in result_data:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
                
    return JsonResponse(result_data, safe=False)