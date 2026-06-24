<!-- src/components/mypage/MyProfileTab.vue -->
<template>
  <div class="my-profile-tab">

    <!-- ① 내 정보 카드 -->
    <section class="info-section">
      <h3 class="section-title"><span class="section-eyebrow">PROFILE</span>내 프로필</h3>

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

      <router-link to="/onboarding" class="btn-edit-survey">설문 다시 작성하기</router-link>
    </section>

    <!-- ② 추천 받기 -->
    <section class="recommend-section">
      <h3 class="section-title"><span class="section-eyebrow">AI MATCH</span>금융상품 추천</h3>

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
        <div
          v-for="(item, idx) in recommendations"
          :key="item.id"
          class="recommend-card"
          @click="goDetail(item.id)"
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

        <button class="btn-retry" @click="fetchRecommendations">다시 추천받기</button>
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

const myInfo     = ref({})
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
  const [infoRes, onboardRes] = await Promise.all([
    getMyInfo(),
    getOnboardingInfo(),
  ])
  myInfo.value = infoRes.data
  onboarding.value = onboardRes.data
})

async function fetchRecommendations() {
  loading.value = true
  message.value = null
  recommendations.value = []
  try {
    const { data } = await getRecommendations()
    recommendations.value = data.recommendations
    message.value = data.message
  } finally {
    loading.value = false
  }
}

const goDetail = (id) => router.push(`/finlife/${id}`)
</script>

<style scoped>
.my-profile-tab { font-family: 'Inter', sans-serif; display: flex; flex-direction: column; gap: 24px; }

.info-section, .recommend-section {
  background: #ffffff;
  border: 1px solid #e1e3e4;
  padding: 28px;
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
  color: #0050cc;
}

/* ── 정보 그리드 ── */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1px;
  background: #e1e3e4;
  border: 1px solid #e1e3e4;
  margin-bottom: 20px;
}
.info-item {
  background: #ffffff;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
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
}
.recommend-card:hover { border-color: #191c1d; }
.card-rank {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #191c1d;
  color: #ffffff;
  font-family: 'Hanken Grotesk', sans-serif;
  font-weight: 700;
  font-size: .85rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
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
}
.btn-retry:hover { background: #191c1d; color: #ffffff; }
</style>