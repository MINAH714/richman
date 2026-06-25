# recommend/services.py
"""
유사도 기반 금융상품 추천 알고리즘

사용자의 온보딩 설문 데이터(UserProfile)를 벡터로 변환하고,
각 예적금 상품(DepositProduct + DepositOption)도 벡터로 변환하여
가중합 방식의 유사도 스코어를 계산한다.

점수 구성 (총 100점 만점):
  1) 투자성향 매칭        - 30점
  2) 가입기간 적합도      - 25점
  3) 금리 매력도          - 25점
  4) 관심자산 매칭        - 20점
"""
from finlife.models import DepositProduct, DepositOption


# ── 사용자 설문값 → 점수 환산 테이블 ──────────────────────────

# 투자성향별로 선호하는 가입기간(개월) 범위
RISK_PREFERRED_TERM = {
    'safe':       (1, 12),    # 안정형 - 단기 선호
    'neutral':    (6, 24),    # 중립형 - 중기 선호
    'aggressive': (12, 36),   # 공격형 - 장기 선호 (높은 금리 위해 묶어둠)
}

# 월 여유자금별로 선호하는 가입기간(개월) 범위
BUDGET_PREFERRED_TERM = {
    'low':   (1, 6),     # 10만 미만 - 짧게
    'mid':   (6, 12),
    'high':  (12, 24),
    'vhigh': (12, 36),   # 100만 이상 - 길게 묶어도 부담 없음
}

# 자산규모별 가중치 (자산이 적을수록 고금리 상품에 더 민감하게 반응)
ASSET_RATE_SENSITIVITY = {
    'low':   1.3,
    'mid':   1.1,
    'high':  1.0,
    'vhigh': 0.9,
}


def _term_score(save_trm, preferred_range):
    """가입기간이 선호 범위 안에 들수록 높은 점수(0~1)"""
    low, high = preferred_range
    if low <= save_trm <= high:
        return 1.0
    # 범위 밖이면 거리에 따라 감점
    distance = min(abs(save_trm - low), abs(save_trm - high))
    return max(0.0, 1.0 - distance / 24)  # 24개월 차이나면 점수 0


def _rate_score(intr_rate2, all_rates):
    """전체 상품 중 금리가 상위권일수록 높은 점수(0~1)"""
    if not all_rates or intr_rate2 is None:
        return 0.0
    max_rate = max(all_rates)
    min_rate = min(all_rates)
    if max_rate == min_rate:
        return 0.5
    return (intr_rate2 - min_rate) / (max_rate - min_rate)


def calculate_score(profile, option, all_rates):
    """
    하나의 DepositOption에 대해 사용자 profile 기준 점수(0~100) 계산
    """
    score = 0.0

    # 1) 투자성향 매칭 (30점)
    risk_range = RISK_PREFERRED_TERM.get(profile.risk_type, (1, 36))
    score += _term_score(option.save_trm, risk_range) * 30

    # 2) 가입기간 적합도 - 월 여유자금 기준 (25점)
    budget_range = BUDGET_PREFERRED_TERM.get(profile.monthly_budget, (1, 36))
    score += _term_score(option.save_trm, budget_range) * 25

    # 3) 금리 매력도 - 자산규모로 가중 (25점)
    sensitivity = ASSET_RATE_SENSITIVITY.get(profile.asset_range, 1.0)
    rate_score = _rate_score(option.intr_rate2, all_rates)
    score += min(1.0, rate_score * sensitivity) * 25

    # 4) 관심자산 매칭 (20점) - 'deposit'(예적금)에 관심 있으면 만점
    interest_assets = profile.interest_assets or []
    if 'deposit' in interest_assets:
        score += 20
    else:
        score += 5  # 관심사가 아니어도 약간의 기본점수는 부여 (완전 배제하지 않음)

    return round(score, 1)


def get_recommendations(profile, limit=5):
    """
    사용자 profile을 기준으로 상위 N개의 (product, option, score) 추천 리스트 반환
    추천 결과가 없으면 빈 리스트 반환
    """
    options = DepositOption.objects.select_related('product').filter(
        intr_rate2__isnull=False
    )

    if not options.exists():
        return []

    all_rates = [opt.intr_rate2 for opt in options if opt.intr_rate2 is not None]

    scored = []
    seen_products = set()  # 같은 상품의 여러 기간 옵션 중 최고점만 채택

    for option in options:
        score = calculate_score(profile, option, all_rates)
        product_id = option.product_id

        existing = next((s for s in scored if s['product'].id == product_id), None)
        if existing:
            if score > existing['score']:
                existing['score'] = score
                existing['option'] = option
        else:
            scored.append({
                'product': option.product,
                'option': option,
                'score': score,
            })

    scored.sort(key=lambda x: -x['score'])
    return scored[:limit]