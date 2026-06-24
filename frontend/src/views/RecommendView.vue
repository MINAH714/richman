<!-- src/views/RecommendView.vue -->
<template>
  <div class="recommend-page">
    <div class="recommend-header">
      <span class="eyebrow">PERSONALIZED</span>
      <h2>나에게 맞는 예적금 추천</h2>
      <p class="subtitle">
        설문에 답해주신 투자성향, 자산규모, 관심자산을 기반으로 추천해드려요.
      </p>
    </div>

    <p v-if="loading" class="status-text">분석 중...</p>

    <div v-else-if="message" class="empty-state">
      <span class="empty-icon">⚠️</span>
      <p>{{ message }}</p>
      <router-link v-if="needsOnboarding" to="/onboarding" class="btn-onboard">
        설문 작성하러 가기
      </router-link>
    </div>

    <div v-else class="recommend-list">
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
          <h3 class="card-name">{{ item.fin_prdt_nm }}</h3>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getRecommendations } from '@/api/recommend'

const router = useRouter()
const recommendations = ref([])
const message = ref(null)
const loading = ref(true)

const needsOnboarding = computed(() => message.value?.includes('온보딩'))

onMounted(async () => {
  try {
    const { data } = await getRecommendations()
    recommendations.value = data.recommendations
    message.value = data.message
  } finally {
    loading.value = false
  }
})

const goDetail = (finPrdtCd) => router.push(`/finlife/${finPrdtCd}`)
</script>

<style scoped>
.recommend-page {
  max-width: 720px;
  margin: 0 auto;
  padding: 48px 24px;
  font-family: 'Inter', sans-serif;
}
.recommend-header { margin-bottom: 32px; }
.eyebrow {
  font-family: 'Geist', sans-serif;
  font-size: 11px;
  letter-spacing: 0.08em;
  color: #0050cc;
  display: block;
  margin-bottom: 10px;
}
.recommend-header h2 {
  font-family: 'Hanken Grotesk', sans-serif;
  font-size: 1.6rem;
  font-weight: 700;
  color: #191c1d;
  margin: 0 0 8px;
}
.subtitle { font-size: .88rem; color: #4c4546; margin: 0; }

.status-text { text-align: center; padding: 4rem; color: #4c4546; }

.empty-state {
  border: 1px solid #e1e3e4;
  background: #ffffff;
  padding: 56px 32px;
  text-align: center;
}
.empty-icon { font-size: 2rem; display: block; margin-bottom: 12px; }
.empty-state p { font-size: .9rem; color: #4c4546; margin: 0 0 20px; line-height: 1.6; }
.btn-onboard {
  display: inline-block;
  padding: 10px 22px;
  background: #191c1d;
  color: #ffffff;
  text-decoration: none;
  font-size: .85rem;
  font-weight: 600;
}
.btn-onboard:hover { background: #0050cc; }

.recommend-list { display: flex; flex-direction: column; gap: 12px; }
.recommend-card {
  display: flex;
  gap: 16px;
  align-items: center;
  border: 1px solid #e1e3e4;
  background: #ffffff;
  padding: 20px;
  cursor: pointer;
  transition: border-color .12s;
}
.recommend-card:hover { border-color: #191c1d; }

.card-rank {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #191c1d;
  color: #ffffff;
  font-family: 'Hanken Grotesk', sans-serif;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.card-body { flex: 1; }
.card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.card-bank { font-size: .76rem; color: #4c4546; font-weight: 600; }
.card-score {
  font-family: 'Geist', sans-serif;
  font-size: 11px;
  color: #0050cc;
  font-weight: 700;
  border: 1px solid #0050cc;
  padding: 2px 8px;
}
.card-name {
  font-family: 'Hanken Grotesk', sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
  color: #191c1d;
  margin: 0 0 6px;
}
.card-meta { font-size: .8rem; color: #4c4546; }
.dot { margin: 0 6px; color: #cfc4c5; }
.best-rate { color: #ba1a1a; font-weight: 700; }
</style>