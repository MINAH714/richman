<template>
  <div class="detail-container">
    <header class="detail-header">
      <button class="back-btn" @click="goBack">← BACK</button>
      <div class="coin-title">
        <h1 class="market-id">{{ marketId }}</h1>
        <span class="status-badge">LIVE</span>
      </div>
    </header>

    <div class="content-grid">
      <section class="chart-section">
        <div class="chart-placeholder">
          <span v-if="isLoading">차트 데이터 로딩 중...</span>
          <span v-else>{{ marketId }} 캔들 차트 영역</span>
        </div>
      </section>

      <aside class="info-section">
        <div class="info-card">
          <h3>현재가 정보</h3>
          <div v-if="coinData" class="price-info">
            <p>가격: {{ coinData.trade_price }}</p>
            <p>변동: {{ coinData.change_rate }}%</p>
          </div>
          <div v-else>데이터를 불러오는 중...</div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
// import { cryptoAPI } from '@/api/crypto' // 백엔드 연동 시 주석 해제

const route = useRoute()
const router = useRouter()

// URL 파라미터에서 마켓 ID (예: KRW-BTC) 가져오기
const marketId = ref(route.params.market)
const isLoading = ref(true)
const coinData = ref(null)

function goBack() {
  router.push('/')
}

async function fetchCoinDetail() {
  isLoading.value = true
  try {
    // 1. 단일 코인 상세 정보 API 호출
    // const detail = await cryptoAPI.getCoinDetail(marketId.value)
    
    // 2. 캔들 차트 데이터 API 호출 (일봉, 분봉 등)
    // const candles = await cryptoAPI.getCandles(marketId.value)
    
    // 임시 더미 데이터 (백엔드 연동 전 화면 확인용)
    coinData.value = { trade_price: 90000000, change_rate: 1.5 }
  } catch (error) {
    console.error('상세 정보 로드 실패:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchCoinDetail()
})
</script>

<style scoped>
/* 임시 스타일링 */
.detail-container {
  min-height: 100vh;
  background: #f0f6ff;
  color: #0f172a;
  padding: 20px;
  font-family: 'IBM Plex Mono', monospace;
}
.detail-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
}
.back-btn {
  padding: 8px 16px;
  background: white;
  border: 1px solid #d0e2f5;
  cursor: pointer;
}
.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}
.chart-placeholder {
  background: white;
  border: 1px solid #e2ecf9;
  height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
}
.info-card {
  background: white;
  border: 1px solid #e2ecf9;
  padding: 20px;
  height: 100%;
}
</style>