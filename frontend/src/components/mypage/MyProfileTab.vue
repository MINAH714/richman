<!-- src/components/mypage/MyProfileTab.vue -->
<template>
  <div class="my-profile-tab">

    <!-- ① 내 정보 카드 -->
    <section class="info-section">
      <h3 class="section-title">
        <span class="section-eyebrow">PROFILE</span>내 프로필
      </h3>

      <div class="info-grid">
        <div class="info-item">
          <span class="info-label">닉네임</span>
          <span class="info-value">{{ myInfo.nickname || '-' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">나이</span>
          <span class="info-value">{{ myInfo.age ? `${myInfo.age}세` : '-' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">이메일</span>
          <span class="info-value">{{ myInfo.email || '-' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">자산 규모</span>
          <span class="info-value">{{ ASSET_LABEL[onboarding.asset_range] || '-' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">투자 성향</span>
          <span class="info-value">{{ RISK_LABEL[onboarding.risk_type] || '-' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">월 여유자금</span>
          <span class="info-value">{{ BUDGET_LABEL[onboarding.monthly_budget] || '-' }}</span>
        </div>
        <div class="info-item info-item--wide">
          <span class="info-label">관심 자산</span>
          <span class="info-value">
            <span
              v-for="tag in onboarding.interest_assets"
              :key="tag"
              class="interest-tag"
            >
              {{ INTEREST_LABEL[tag] || tag }}
            </span>
            <span v-if="!onboarding.interest_assets?.length">-</span>
          </span>
        </div>
      </div>
    </section>

    <!-- ② 추천 받기 -->
    <section class="recommend-section">
      <h3 class="section-title">
        <span class="section-eyebrow">AI MATCH</span>금융상품 추천
      </h3>

      <button
        v-if="!recommendations.length && !loading"
        class="btn-recommend"
        @click="fetchRecommendations"
      >
        금융상품 추천 받기
      </button>

      <p v-if="loading" class="status-text">분석 중...</p>

      <p v-if="message" class="empty-message">{{ message }}</p>

      <div v-if="recommendations.length" class="recommend-list">
        <!-- 🎯 [교정 완료] :key와 @click 인자를 고유 코드(fin_prdt_cd)로 연결해 404 에러 원천 차단 -->
        <div
          v-for="(item, idx) in recommendations"
          :key="item.fin_prdt_cd"
          class="recommend-card"
          @click="goDetail(item.fin_prdt_cd)"
        >
          <div class="card-rank">{{ idx + 1 }}</div>
          <div class="card-body">
            <div class="card-top">
              <span class="card-bank">{{ item.kor_co_nm }}</span>
              <span class="card-score">매칭 {{ item.score }}점</span>
            </div>
            <h4 class="card-name">{{ item.fin_prdt_nm }}</h4>
            <div class="card-meta">
              <span>{{ item.save_trm }}개월</span>
              <span class="dot">·</span>
              <span>기본 {{ item.intr_rate }}%</span>
              <span class="dot">·</span>
              <span class="best-rate">최고 {{ item.intr_rate2 }}%</span>
            </div>
          </div>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getMyInfo, getOnboardingInfo } from '@/api/accounts'
import { getRecommendations } from '@/api/recommend'

const router = useRouter()

const myInfo = ref({})
const onboarding = ref({})
const recommendations = ref([])
const message = ref(null)
const loading = ref(false)

const ASSET_LABEL = {
  low: '500만 미만', mid: '500만~2,000만', high: '2,000만~5,000만', vhigh: '5,000만 이상',
}
const RISK_LABEL = {
  safe: '안정형', neutral: '중립형', aggressive: '공격형',
}
const BUDGET_LABEL = {
  low: '10만 미만', mid: '10~50만', high: '50~100만', vhigh: '100만 이상',
}
const INTEREST_LABEL = {
  deposit: '예/적금', stock: '주식', crypto: '코인', gold: '금/은',
}

onMounted(async () => {
  try {
    const [infoRes, onboardRes] = await Promise.all([
      getMyInfo(),
      getOnboardingInfo(),
    ])
    myInfo.value = infoRes.data
    onboarding.value = onboardRes.data
  } catch (error) {
    console.error("내 프로필 정보 로드 실패:", error)
  }
})

async function fetchRecommendations() {
  loading.value = true
  message.value = null
  recommendations.value = []
  try {
    const { data } = await getRecommendations()
    recommendations.value = data.recommendations
    message.value = data.message
  } catch (error) {
    console.error("추천 데이터 패치 오류:", error)
  } finally {
    loading.value = false
  }
}

// 🎯 [교정 완료] 백엔드 및 상세 뷰 라우팅 규칙에 대응하도록 고유 코드 기반 리다이렉트 처리
const goDetail = (finPrdtCd) => {
  router.push(`/finlife/${finPrdtCd}`)
}
</script>

<style scoped>
/* ── 마이페이지 전용 모노톤 하드엣지 디자인 가이드 동기화 ── */
.my-profile-tab {
  font-family: 'Inter', 'Geist', 'Hanken Grotesk', sans-serif;
  display: flex;
  flex-direction: column;
  gap: 24px;
  box-sizing: border-box;
}

.my-profile-tab * {
  box-sizing: border-box;
}

.info-section, .recommend-section {
  background: #ffffff;
  border: 1px solid #e1e3e4; /* 하이라인 테두리 유지 */
  padding: 28px;
  border-radius: 0px !important; /* 모노톤 하드엣지: 라운드 제거 */
  box-shadow: none !important;    /* 모노톤 하드엣지: 그림자 제거 */
}

.section-title {
  font-family: 'Hanken Grotesk', sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
  margin: 0 0 20px;
  color: #191c1d;
  display: flex;
  align-items: baseline;
  gap: 10px;
}
.section-eyebrow {
  font-family: 'Geist', sans-serif;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.08em;
  color: #0050cc; /* 포인트 블루 브랜드 컬러 유지 */
}

/* ── 정보 그리드 ── */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1px;
  background: #e1e3e4;
  border: 1px solid #e1e3e4;
  margin-bottom: 20px;
  border-radius: 0px !important;
}
.info-item {
  background: #ffffff;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  border-radius: 0px !important;
}
.info-item--wide { grid-column: 1 / -1; }
.info-label {
  font-family: 'Geist', sans-serif;
  font-size: 10px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #4c4546;
}
.info-value { font-size: .9rem; font-weight: 600; color: #191c1d; }

.interest-tag {
  display: inline-block;
  font-size: .76rem;
  border: 1px solid #cfc4c5;
  padding: 2px 8px;
  margin-right: 6px;
  font-weight: 500;
  border-radius: 0px !important;
}

.btn-edit-survey {
  display: inline-block;
  font-size: .8rem;
  color: #4c4546;
  text-decoration: none;
  border-bottom: 1px solid #cfc4c5;
}
.btn-edit-survey:hover { color: #0050cc; border-color: #0050cc; }

/* ── 추천 섹션 ── */
.btn-recommend {
  width: 100%;
  padding: 16px;
  background: #191c1d;
  color: #ffffff;
  border: none;
  font-size: .95rem;
  font-weight: 700;
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  transition: background .12s;
  border-radius: 0px !important;
}
.btn-recommend:hover { background: #0050cc; }

.status-text { text-align: center; padding: 2rem; color: #4c4546; font-size: .85rem; }
.empty-message {
  text-align: center;
  padding: 1.5rem;
  color: #4c4546;
  font-size: .85rem;
  border: 1px solid #e1e3e4;
  background: #f8f9fa;
  border-radius: 0px !important;
}

.recommend-list { display: flex; flex-direction: column; gap: 10px; }
.recommend-card {
  display: flex;
  gap: 14px;
  align-items: center;
  border: 1px solid #e1e3e4;
  padding: 16px;
  cursor: pointer;
  transition: border-color .12s;
  border-radius: 0px !important;
}
.recommend-card:hover { border-color: #191c1d; }

.card-rank {
  width: 28px;
  height: 28px;
  background: #191c1d;
  color: #ffffff;
  font-family: 'Hanken Grotesk', sans-serif;
  font-weight: 700;
  font-size: .85rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border-radius: 0px !important; /* 동그라미 제거하여 사각형의 하드엣지 감성 극대화 */
}
.card-body { flex: 1; }
.card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.card-bank { font-size: .74rem; color: #4c4546; font-weight: 600; }
.card-score {
  font-family: 'Geist', sans-serif;
  font-size: 10px;
  color: #0050cc;
  font-weight: 700;
  border: 1px solid #0050cc;
  padding: 1px 7px;
  border-radius: 0px !important;
}
.card-name {
  font-family: 'Hanken Grotesk', sans-serif;
  font-size: .98rem;
  font-weight: 700;
  color: #191c1d;
  margin: 0 0 4px;
}
.card-meta { font-size: .78rem; color: #4c4546; }
.dot { margin: 0 6px; color: #cfc4c5; }
.best-rate { color: #ba1a1a; font-weight: 700; }

.btn-retry {
  margin-top: 8px;
  padding: 10px;
  background: #ffffff;
  border: 1px solid #191c1d;
  color: #191c1d;
  font-size: .82rem;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  transition: background .12s, color .12s;
  border-radius: 0px !important;
}
.btn-retry:hover { background: #191c1d; color: #ffffff; }
</style>