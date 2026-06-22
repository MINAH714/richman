<template>
  <div class="detail-container">

    <header class="detail-header">
      <button class="back-btn" @click="router.back()">← BACK</button>
      <div class="coin-title">
        <h1 class="market-id">{{ symbol }}</h1>
        <span class="status-badge">LIVE</span>
      </div>
      <button
        class="fav-btn"
        :class="{ active: isWatched }"
        @click="handleWatchlistToggle"
      >
        {{ isWatched ? '★ 관심 종목 해제' : '☆ 관심 종목 추가' }}
      </button>
    </header>

    <div class="content-grid">

      <section class="chart-section">
        
        <div class="chart-toolbar">
          <div class="period-tabs">
            <button
              v-for="p in periods"
              :key="p.value"
              :class="['tab', { active: selectedPeriod === p.value }]"
              @click="changePeriod(p.value)"
            >
              {{ p.label }}
            </button>
          </div>

          <div class="indicator-toggles">
            <label v-for="ind in indicators" :key="ind.key" class="toggle-label">
              <input type="checkbox" v-model="ind.visible" />
              <span :style="{ color: ind.color, fontWeight: ind.visible ? 'bold' : 'normal' }">
                {{ ind.label }}
              </span>
            </label>
          </div>
        </div>

        <div v-if="isLoading" class="chart-placeholder">
          <span>📡 차트 데이터를 불러오는 중...</span>
        </div>
        <div v-else-if="error" class="chart-placeholder error">
          <span>⚠️ {{ error }}</span>
        </div>

        <template v-else-if="chartData">
          <div class="chart-wrap">
            <apexchart
              type="candlestick"
              height="420"
              :options="candleOptions"
              :series="candleSeries"
            />
          </div>

          <div class="chart-wrap volume-wrap">
            <apexchart
              type="bar"
              height="150"
              :options="volumeOptions"
              :series="volumeSeries"
            />
          </div>
        </template>
        
        <p class="disclaimer">
          ⚠️ 이 차트는 참고용 정보이며, 투자 권유가 아닙니다. 투자에는 항상 위험이 따릅니다.
        </p>
      </section>

      <aside class="info-section">

        <div class="info-card">
          <h3>현재가 정보</h3>
          <div v-if="isPriceLoading" class="info-loading">불러오는 중...</div>
          <div v-else-if="stockPrice" class="price-info">
            <div class="info-row">
              <span class="info-label">현재가</span>
              <span class="info-value price">{{ formatPrice(stockPrice.current_price) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">등락률</span>
              <span class="info-value" :class="changeClass(stockPrice.change_rate)">
                {{ formatRate(stockPrice.change_rate) }}
              </span>
            </div>
            <div class="info-row">
              <span class="info-label">고가</span>
              <span class="info-value up">{{ formatPrice(stockPrice.high_price) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">저가</span>
              <span class="info-value down">{{ formatPrice(stockPrice.low_price) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">거래량(24h)</span>
              <span class="info-value">{{ formatVolume(stockPrice.volume) }}</span>
            </div>
          </div>
          <div v-else-if="latestCandle" class="price-info">
             <div class="info-row">
              <span class="info-label">현재가(종가)</span>
              <span class="info-value price">{{ formatPrice(latestCandle.y[3]) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">고가</span>
              <span class="info-value up">{{ formatPrice(latestCandle.y[1]) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">저가</span>
              <span class="info-value down">{{ formatPrice(latestCandle.y[2]) }}</span>
            </div>
          </div>
          <div v-else class="info-loading">데이터가 없습니다.</div>
        </div>

        <div class="info-card">
          <h3>종목 정보</h3>
          <div class="info-row">
            <span class="info-label">마켓</span>
            <span class="info-value">{{ stockPrice?.market || 'KRX' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">심볼</span>
            <span class="info-value">{{ symbol }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">종목명</span>
            <span class="info-value">{{ stockPrice?.name || symbol }}</span>
          </div>
        </div>

      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import VueApexCharts from 'vue3-apexcharts'
// 💡 stocks API에서 가격을 가져오는 함수도 import 합니다 (구현되어 있다면)
import { getStockChart, getStockPrice } from '@/api/stocks' 
import { useWatchlistStore } from '@/stores/watchlist'

const apexchart = VueApexCharts
const route  = useRoute()
const router = useRouter()
const watchlistStore = useWatchlistStore()

const symbol = route.params.symbol

// ── 차트 상태 ──
const chartData      = ref(null)
const isLoading      = ref(false)
const error          = ref(null)
const selectedPeriod = ref('3mo')

// ── 가격 패널 상태 ──
const stockPrice     = ref(null)
const isPriceLoading = ref(false)

// ── 탭 & 지표 토글 설정 ──
const periods = [
  { label: '1개월', value: '1mo' },
  { label: '3개월', value: '3mo' },
  { label: '6개월', value: '6mo' },
  { label: '1년',   value: '1y'  },
]

const indicators = ref([
  { key: 'ma5',  label: 'MA5',  color: '#f59e0b', visible: true  },
  { key: 'ma20', label: 'MA20', color: '#10b981', visible: true  },
  { key: 'ma60', label: 'MA60', color: '#8b5cf6', visible: false },
  { key: 'bb',   label: '볼린저밴드', color: '#94a3b8', visible: false },
])

// 관심 종목 연동
const isWatched = computed(() =>
  watchlistStore.watchedSymbols.includes(symbol)
)

async function handleWatchlistToggle() {
  if (isWatched.value) {
    router.push({ name: 'stock-watchlist' })
  } else {
    await watchlistStore.addToWatchlist({
      symbol,
      name: stockPrice.value?.name || symbol,
      market: stockPrice.value?.market || 'KRX',
    })
  }
}

// ── API 호출 로직 ──
async function fetchChart() {
  isLoading.value = true
  error.value     = null
  try {
    const res = await getStockChart(symbol, selectedPeriod.value)
    chartData.value = res.data
  } catch (err) {
    error.value = '차트 데이터를 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

// 우측 사이드 패널용 현재가 정보 호출 (API가 있을 경우)
async function fetchPriceInfo() {
  isPriceLoading.value = true
  try {
    const res = await getStockPrice(symbol)
    stockPrice.value = res.data
  } catch (err) {
    console.warn('현재가 정보를 가져오지 못했습니다. 차트 데이터로 대체합니다.')
  } finally {
    isPriceLoading.value = false
  }
}

function changePeriod(period) {
  selectedPeriod.value = period
}
watch(selectedPeriod, fetchChart)

// 데이터가 없을 때 우측 패널에 표시할 최신 캔들 데이터 추출
const latestCandle = computed(() => {
  if (!chartData.value || !chartData.value.candle) return null
  const candles = chartData.value.candle
  return candles[candles.length - 1]
})

// ── 차트 데이터 시리즈 세팅 ──
const candleSeries = computed(() => {
  if (!chartData.value) return []
  const series = [
    { name: '주가', type: 'candlestick', data: chartData.value.candle }
  ]
  const ind = indicators.value
  if (ind.find(i => i.key === 'ma5')?.visible) {
    series.push({
      name: 'MA5', type: 'line',
      data: chartData.value.dates.map((d, i) => ({ x: d, y: chartData.value.ma.ma5[i] }))
    })
  }
  if (ind.find(i => i.key === 'ma20')?.visible) {
    series.push({
      name: 'MA20', type: 'line',
      data: chartData.value.dates.map((d, i) => ({ x: d, y: chartData.value.ma.ma20[i] }))
    })
  }
  if (ind.find(i => i.key === 'ma60')?.visible) {
    series.push({
      name: 'MA60', type: 'line',
      data: chartData.value.dates.map((d, i) => ({ x: d, y: chartData.value.ma.ma60[i] }))
    })
  }
  if (ind.find(i => i.key === 'bb')?.visible) {
    series.push(
      { name: 'BB 상단', type: 'line', data: chartData.value.dates.map((d, i) => ({ x: d, y: chartData.value.bollinger.upper[i] })) },
      { name: 'BB 중간', type: 'line', data: chartData.value.dates.map((d, i) => ({ x: d, y: chartData.value.bollinger.mid[i] })) },
      { name: 'BB 하단', type: 'line', data: chartData.value.dates.map((d, i) => ({ x: d, y: chartData.value.bollinger.lower[i] })) }
    )
  }
  return series
})

// ── 차트 옵션 세팅 ──
const candleOptions = computed(() => ({
  chart: {
    id: 'candle-chart',
    type: 'candlestick',
    toolbar: { show: true },
    zoom: { enabled: true },
    background: 'transparent',
  },
  colors: ['#2563eb', '#f59e0b', '#10b981', '#8b5cf6', '#94a3b8', '#94a3b8', '#94a3b8'],
  stroke: { width: [1, 2, 2, 2, 1, 1, 1] },
  xaxis: {
    type: 'category',
    labels: { rotate: -45, style: { fontFamily: 'IBM Plex Mono, monospace', fontSize: '11px' } },
  },
  yaxis: {
    tooltip: { enabled: true },
    labels: { formatter: (val) => val != null ? val.toLocaleString('ko-KR') : '' }
  },
  tooltip: { shared: true, custom: undefined },
  plotOptions: {
    candlestick: {
      colors: { upward: '#ef4444', downward: '#3b82f6' }
    }
  },
  legend: { show: false }, // 범례는 헤더 토글로 대체하므로 끔
  grid: { borderColor: '#e2ecf9' },
}))

const volumeSeries = computed(() => {
  if (!chartData.value) return []
  return [{
    name: '거래량',
    data: chartData.value.dates.map((d, i) => ({ x: d, y: chartData.value.volume[i] }))
  }]
})

const volumeOptions = computed(() => ({
  chart: {
    id: 'volume-chart',
    type: 'bar',
    toolbar: { show: false },
    brush: { target: 'candle-chart', enabled: true },
    background: 'transparent',
  },
  colors: ['#94a3b8'],
  xaxis: { type: 'category', labels: { show: false } },
  yaxis: {
    labels: {
      formatter: (val) => {
        if (val >= 1_000_000) return (val / 1_000_000).toFixed(1) + 'M'
        if (val >= 1_000)     return (val / 1_000).toFixed(0) + 'K'
        return val
      }
    }
  },
  dataLabels: { enabled: false },
  plotOptions: { bar: { columnWidth: '80%' } },
  grid: { borderColor: '#e2ecf9' },
}))

// ── 라이프사이클 ──
onMounted(() => {
  watchlistStore.fetchWatchlist()
  fetchChart()
  fetchPriceInfo() // 패널 정보 API 호출
})

// ── 포맷 헬퍼 (Crypto 파일 참고) ──
function formatPrice(price) {
  if (price == null) return '-'
  return price.toLocaleString('ko-KR') + ' 원'
}
function formatRate(rate) {
  if (rate == null) return '-'
  return (rate > 0 ? '+' : '') + rate.toFixed(2) + '%'
}
function formatVolume(vol) {
  if (vol == null) return '-'
  return vol.toLocaleString('ko-KR')
}
function changeClass(change) {
  if (change > 0) return 'up'
  if (change < 0) return 'down'
  return 'flat'
}
</script>

<style scoped>
/* ── 글로벌 컨테이너 ── */
.detail-container {
  min-height: 100vh;
  background: #f0f6ff;
  color: #0f172a;
  padding: 24px;
  font-family: 'IBM Plex Mono', 'Pretendard', sans-serif;
}

/* ── 헤더 영역 ── */
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
  border-radius: 6px;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.85rem;
  font-weight: 600;
  transition: background 0.15s;
}
.back-btn:hover { background: #e8f0fe; }
.coin-title { display: flex; align-items: center; gap: 10px; flex: 1; }
.market-id  { font-size: 1.5rem; font-weight: 800; margin: 0; }
.status-badge {
  padding: 3px 8px;
  background: #dcfce7;
  color: #16a34a;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 700;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.5; }
}
.fav-btn {
  padding: 8px 16px;
  border: 1px solid #d0e2f5;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.85rem;
  font-weight: 600;
  color: #6b7280;
  transition: all 0.2s;
}
.fav-btn.active { background: #fef3c7; border-color: #f59e0b; color: #d97706; }
.fav-btn:hover  { opacity: 0.8; }

/* ── 메인 그리드 레이아웃 ── */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 320px; /* 좌측 차트, 우측 패널 */
  gap: 20px;
  align-items: start;
}

/* ── 좌측 차트 섹션 ── */
.chart-section {
  background: white;
  border: 1px solid #e2ecf9;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}
.chart-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f1f5f9;
}
.period-tabs {
  display: flex;
  gap: 8px;
}
.tab {
  padding: 6px 16px;
  border: 1px solid #e2ecf9;
  border-radius: 99px;
  background: #f8fafc;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  color: #64748b;
  transition: all 0.2s;
}
.tab.active { background: #2563eb; color: #fff; border-color: #2563eb; }
.tab:hover:not(.active) { background: #e2ecf9; }

.indicator-toggles {
  display: flex;
  gap: 16px;
}
.toggle-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  cursor: pointer;
  color: #475569;
}
.toggle-label input { accent-color: #2563eb; }

.chart-placeholder {
  height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-weight: 600;
}
.chart-placeholder.error { color: #ef4444; }

.chart-wrap { margin-bottom: 10px; }
.volume-wrap { margin-bottom: 0; }
.disclaimer {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 24px;
  text-align: center;
}

/* ── 우측 정보 패널 섹션 ── */
.info-section { 
  display: flex; 
  flex-direction: column; 
  gap: 16px; 
}
.info-card {
  background: white;
  border: 1px solid #e2ecf9;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}
.info-card h3 {
  font-size: 0.9rem;
  font-weight: 700;
  color: #475569;
  margin: 0 0 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
}
.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px dashed #f1f5f9;
  font-size: 0.9rem;
}
.info-row:last-child { border-bottom: none; padding-bottom: 0; }
.info-label { color: #64748b; font-weight: 500; }
.info-value { font-weight: 700; color: #1e293b; }
.info-value.price { font-size: 1.1rem; }
.info-loading { color: #94a3b8; font-size: 0.85rem; padding: 10px 0; text-align: center; }

/* 증감 색상 (한국 주식/코인 기준) */
.up   { color: #ef4444; } /* 상승 빨강 */
.down { color: #3b82f6; } /* 하락 파랑 */
.flat { color: #64748b; }

/* ── 반응형 (모바일 등) ── */
@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr; /* 좁아지면 우측 패널이 차트 밑으로 내려감 */
  }
}
</style>