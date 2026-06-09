<!-- frontend/src/views/CryptoDetailView.vue -->
<template>
  <div class="detail-container">

    <!-- ── 헤더 ───────────────────────────────────────────── -->
    <header class="detail-header">
      <button class="back-btn" @click="goBack">← BACK</button>
      <div class="coin-title">
        <h1 class="market-id">{{ marketId }}</h1>
        <span class="status-badge">LIVE</span>
      </div>
      <!-- 즐겨찾기 버튼 (로그인 시) -->
      <button
        v-if="authStore.isLoggedIn"
        class="fav-btn"
        :class="{ active: cryptoStore.watchlistSymbols.has(coinSymbol) }"
        @click="cryptoStore.toggleWatchlist(coinSymbol)"
      >
        {{ cryptoStore.watchlistSymbols.has(coinSymbol) ? '★ 즐겨찾기 해제' : '☆ 즐겨찾기' }}
      </button>
    </header>

    <!-- ── 메인 그리드 ─────────────────────────────────────── -->
    <div class="content-grid">

      <!-- 캔들 차트 -->
      <section class="chart-section">
        <div v-if="isLoading" class="chart-placeholder">
          <span>차트 데이터 로딩 중...</span>
        </div>
        <div v-else-if="candles.length === 0" class="chart-placeholder">
          <span>캔들 데이터가 없습니다.</span>
        </div>
        <apexchart
          v-else
          type="candlestick"
          height="500"
          :options="chartOptions"
          :series="chartSeries"
        />
      </section>

      <!-- 현재가 정보 -->
      <aside class="info-section">
        <div class="info-card">
          <h3>현재가 정보</h3>

          <div v-if="isLoading" class="info-loading">불러오는 중...</div>

          <div v-else-if="ticker" class="price-info">
            <div class="info-row">
              <span class="info-label">현재가</span>
              <span class="info-value price">
                {{ formatPrice(ticker.trade_price) }}
              </span>
            </div>
            <div class="info-row">
              <span class="info-label">등락률</span>
              <span class="info-value" :class="changeClass(ticker.change)">
                {{ formatRate(ticker.change_rate) }}
              </span>
            </div>
            <div class="info-row">
              <span class="info-label">전일대비</span>
              <span class="info-value" :class="changeClass(ticker.change)">
                {{ formatPrice(ticker.signed_change_price) }}
              </span>
            </div>
            <div class="info-row">
              <span class="info-label">고가</span>
              <span class="info-value up">{{ formatPrice(ticker.high_price) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">저가</span>
              <span class="info-value down">{{ formatPrice(ticker.low_price) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">거래대금(24h)</span>
              <span class="info-value">{{ formatVolume(ticker.acc_trade_price_24h) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">거래량(24h)</span>
              <span class="info-value">
                {{ ticker.acc_trade_volume_24h?.toFixed(3) }}
              </span>
            </div>
          </div>

          <div v-else class="info-loading">데이터를 불러오는 중...</div>
        </div>

        <!-- 코인 기본 정보 -->
        <div class="info-card mt">
          <h3>코인 정보</h3>
          <div class="info-row">
            <span class="info-label">마켓</span>
            <span class="info-value">{{ marketId }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">심볼</span>
            <span class="info-value">{{ coinSymbol }}</span>
          </div>
          <div v-if="coinMeta" class="info-row">
            <span class="info-label">한글명</span>
            <span class="info-value">{{ coinMeta.korean_name }}</span>
          </div>
          <div v-if="coinMeta" class="info-row">
            <span class="info-label">영문명</span>
            <span class="info-value">{{ coinMeta.english_name }}</span>
          </div>
        </div>
      </aside>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import VueApexCharts from 'vue3-apexcharts'
import { useCryptoStore } from '@/stores/crypto'
import { useAuthStore } from '@/stores/auth'
import { cryptoAPI } from '@/api/crypto'

const apexchart = VueApexCharts

const route = useRoute()
const router = useRouter()
const cryptoStore = useCryptoStore()
const authStore = useAuthStore()

const marketId = ref(route.params.market)           // KRW-BTC
const coinSymbol = computed(() => marketId.value.split('-')[1])  // BTC

const isLoading = ref(true)
const ticker = ref(null)
const candles = ref([])

// 코인 메타 (한글명 등) — store에서 찾기
const coinMeta = computed(() =>
  cryptoStore.coins.find(c => c.market === marketId.value) ?? null
)

// ── ApexCharts 설정 ────────────────────────────────────────
const chartOptions = computed(() => ({
  chart: {
    type: 'candlestick',
    background: 'transparent',
    toolbar: { show: true },
    zoom: { enabled: true },
  },
  theme: { mode: 'light' },
  xaxis: {
    type: 'datetime',
    labels: {
      style: { fontFamily: 'IBM Plex Mono, monospace', fontSize: '11px' },
    },
  },
  yaxis: {
    tooltip: { enabled: true },
    labels: {
      formatter: (val) => val?.toLocaleString('ko-KR'),
      style: { fontFamily: 'IBM Plex Mono, monospace', fontSize: '11px' },
    },
  },
  plotOptions: {
    candlestick: {
      colors: {
        upward: '#ef4444',    // 상승 — 빨강 (한국식)
        downward: '#3b82f6',  // 하락 — 파랑 (한국식)
      },
    },
  },
  tooltip: {
    x: { format: 'yyyy-MM-dd' },
  },
  grid: {
    borderColor: '#e2ecf9',
  },
}))

const chartSeries = computed(() => [{
  name: marketId.value,
  data: candles.value.map(c => ({
    x: new Date(c.candle_date_time_kst),
    y: [c.opening_price, c.high_price, c.low_price, c.trade_price],
  })),
}])

// ── API 호출 ──────────────────────────────────────────────
async function fetchCoinDetail() {
  isLoading.value = true
  try {
    const { data } = await cryptoAPI.getCoinDetail(marketId.value)
    ticker.value = data.ticker
    candles.value = data.candles
  } catch (error) {
    console.error('상세 정보 로드 실패:', error)
  } finally {
    isLoading.value = false
  }
}

// ── 10초 폴링 (ticker만) ──────────────────────────────────
let pollingTimer = null

async function pollTicker() {
  try {
    const { data } = await cryptoAPI.getCoinDetail(marketId.value)
    ticker.value = data.ticker
  } catch (e) {
    console.error('ticker 폴링 실패:', e)
  }
}

function goBack() {
  router.push('/crypto')
}

onMounted(async () => {
  // store에 코인 목록 없으면 로드 (한글명 표시용)
  if (cryptoStore.coins.length === 0) await cryptoStore.loadCoins()
  if (authStore.isLoggedIn && cryptoStore.watchlist.length === 0) {
    await cryptoStore.loadWatchlist()
  }
  await fetchCoinDetail()
  pollingTimer = setInterval(pollTicker, 10_000)
})

onUnmounted(() => {
  clearInterval(pollingTimer)
})

// ── 포맷 헬퍼 ────────────────────────────────────────────
function formatPrice(price) {
  if (price == null) return '-'
  return price >= 100
    ? price.toLocaleString('ko-KR') + ' 원'
    : price.toFixed(4) + ' 원'
}

function formatRate(rate) {
  if (rate == null) return '-'
  return (rate >= 0 ? '+' : '') + (rate * 100).toFixed(2) + '%'
}

function formatVolume(vol) {
  if (vol == null) return '-'
  if (vol >= 1_000_000_000_000) return (vol / 1_000_000_000_000).toFixed(1) + '조'
  if (vol >= 100_000_000) return (vol / 100_000_000).toFixed(1) + '억'
  return vol.toLocaleString('ko-KR')
}

function changeClass(change) {
  if (change === 'RISE') return 'up'
  if (change === 'FALL') return 'down'
  return 'flat'
}
</script>

<style scoped>
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
  border-radius: 4px;
  cursor: pointer;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.85rem;
  transition: background 0.15s;
}
.back-btn:hover { background: #e8f0fe; }

.coin-title {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}
.market-id { font-size: 1.5rem; font-weight: 700; margin: 0; }
.status-badge {
  padding: 2px 8px;
  background: #dcfce7;
  color: #16a34a;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.fav-btn {
  padding: 8px 16px;
  border: 1px solid #d0e2f5;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.85rem;
  color: #6b7280;
  transition: all 0.15s;
}
.fav-btn.active {
  background: #fef3c7;
  border-color: #f59e0b;
  color: #d97706;
}
.fav-btn:hover { opacity: 0.8; }

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.chart-section {
  background: white;
  border: 1px solid #e2ecf9;
  border-radius: 8px;
  padding: 16px;
}

.chart-placeholder {
  height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
}

.info-section { display: flex; flex-direction: column; gap: 16px; }

.info-card {
  background: white;
  border: 1px solid #e2ecf9;
  border-radius: 8px;
  padding: 20px;
}
.info-card h3 {
  font-size: 0.85rem;
  font-weight: 600;
  color: #6b7280;
  margin: 0 0 16px 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.85rem;
}
.info-row:last-child { border-bottom: none; }
.info-label { color: #94a3b8; }
.info-value { font-weight: 600; }
.info-value.price { font-size: 1rem; }

.info-loading { color: #94a3b8; font-size: 0.85rem; padding: 8px 0; }

.up { color: #ef4444; }
.down { color: #3b82f6; }
.flat { color: #6b7280; }
</style>