<!-- src/views/StockChartView.vue -->
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

      <!-- ── 좌측 차트 섹션 ── -->
      <section class="chart-section">

        <div class="chart-toolbar">
          <!-- 캔들 단위 탭 -->
          <div class="period-tabs">
            <button
              v-for="iv in intervals"
              :key="iv.value"
              :class="['tab', { active: selectedInterval === iv.value }]"
              @click="changeInterval(iv.value)"
            >{{ iv.label }}</button>
          </div>

          <!-- 지표 토글 -->
          <div class="indicator-toggles">
            <label v-for="ind in indicators" :key="ind.key" class="toggle-label">
              <input type="checkbox" v-model="ind.visible" />
              <span :style="{ color: ind.color, fontWeight: ind.visible ? 'bold' : 'normal' }">
                {{ ind.label }}
              </span>
            </label>
          </div>
        </div>

        <!-- 로딩 / 에러 -->
        <div v-if="isLoading" class="chart-placeholder">
          <span>📡 차트 데이터를 불러오는 중...</span>
        </div>
        <div v-else-if="error" class="chart-placeholder error">
          <span>⚠️ {{ error }}</span>
        </div>

        <!-- 차트 영역 -->
        <template v-else-if="chartData">

          <!-- 줌 정보 표시 -->
          <div class="zoom-info">
            <span class="zoom-count">📊 {{ visibleCount }}개 캔들</span>
            <span class="zoom-hint">🖱️ 마우스 휠로 확대/축소</span>
          </div>

          <!-- 💡 wheel 이벤트를 잡을 래퍼 div -->
          <div class="chart-zoom-wrap" ref="chartWrapRef">

            <!-- 캔들스틱 차트 -->
            <div class="chart-wrap">
              <apexchart
                ref="candleChartRef"
                type="candlestick"
                height="400"
                :options="candleOptions"
                :series="candleSeries"
              />
            </div>

            <!-- 거래량 차트 -->
            <div class="chart-wrap volume-wrap">
              <apexchart
                ref="volumeChartRef"
                type="bar"
                height="140"
                :options="volumeOptions"
                :series="volumeSeries"
              />
            </div>

          </div>
        </template>

        <p class="disclaimer">
          ⚠️ 이 차트는 참고용 정보이며, 투자 권유가 아닙니다. 투자에는 항상 위험이 따릅니다.
        </p>
      </section>

      <!-- ── 우측 정보 패널 ── -->
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
          </div>
          <div v-else-if="latestCandle" class="price-info">
            <div class="info-row">
              <span class="info-label">종가</span>
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
            <span class="info-label">심볼</span>
            <span class="info-value">{{ symbol }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">캔들 단위</span>
            <span class="info-value">
              {{ intervals.find(i => i.value === selectedInterval)?.label }}봉
            </span>
          </div>
        </div>
      </aside>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import VueApexCharts from 'vue3-apexcharts'
import { getStockChart, getStockPrice } from '@/api/stocks'
import { useWatchlistStore } from '@/stores/watchlist'

const apexchart = VueApexCharts
const route  = useRoute()
const router = useRouter()
const watchlistStore = useWatchlistStore()
const symbol = route.params.symbol

// ── 차트 상태 ──────────────────────────────────────────
const chartData      = ref(null)
const isLoading      = ref(false)
const error          = ref(null)
const selectedInterval = ref('1d')

// ── 가격 패널 상태 ────────────────────────────────────
const stockPrice     = ref(null)
const isPriceLoading = ref(false)

// ── 차트 컴포넌트 ref ──────────────────────────────────
const chartWrapRef   = ref(null)   // wheel 이벤트 등록 대상
const candleChartRef = ref(null)
const volumeChartRef = ref(null)

// ── 휠 줌 상태 ────────────────────────────────────────
const visibleCount = ref(50)       // 현재 보이는 캔들 개수 (기본 50개)
const MIN_VISIBLE  = 10            // 최소 10개
const MAX_VISIBLE  = 200           // 최대 200개

// ── 캔들 단위 탭 ──────────────────────────────────────
const intervals = [
  { label: '1일',  value: '1d'  },
  { label: '1주',  value: '1wk' },
  { label: '1달',  value: '1mo' },
  { label: '1년',  value: '3mo' },
]

// ── 지표 토글 ─────────────────────────────────────────
const indicators = ref([
  { key: 'ma5',  label: 'MA5',      color: '#f59e0b', visible: true  },
  { key: 'ma20', label: 'MA20',     color: '#10b981', visible: true  },
  { key: 'ma60', label: 'MA60',     color: '#8b5cf6', visible: false },
  { key: 'bb',   label: '볼린저밴드', color: '#94a3b8', visible: false },
])

// ── 관심 종목 연동 ────────────────────────────────────
const isWatched = computed(() =>
  watchlistStore.watchedSymbols.includes(symbol)
)

async function handleWatchlistToggle() {
  if (isWatched.value) {
    router.push({ name: 'stock-watchlist' })
  } else {
    await watchlistStore.addToWatchlist({
      symbol,
      name:   stockPrice.value?.name   || symbol,
      market: stockPrice.value?.market || 'KRX',
    })
  }
}

// ── 현재 보이는 데이터 슬라이싱 ──────────────────────
// 전체 데이터에서 뒤쪽(최신) 기준으로 visibleCount개만 잘라냄
const visibleData = computed(() => {
  if (!chartData.value) return null

  const total    = chartData.value.dates.length
  const count    = Math.min(visibleCount.value, total)
  const startIdx = total - count    // 맨 뒤에서 count개

  const sl = (arr) => arr.slice(startIdx, total)

  return {
    dates:    sl(chartData.value.dates),
    candle:   sl(chartData.value.candle),
    volume:   sl(chartData.value.volume),
    ma: {
      ma5:  sl(chartData.value.ma.ma5),
      ma20: sl(chartData.value.ma.ma20),
      ma60: sl(chartData.value.ma.ma60),
    },
    bollinger: {
      upper: sl(chartData.value.bollinger.upper),
      mid:   sl(chartData.value.bollinger.mid),
      lower: sl(chartData.value.bollinger.lower),
    },
  }
})

// ── 거래량 바 색상 계산 ───────────────────────────────
// 캔들 종가 >= 시가 → 상승(빨강), 아니면 하락(파랑)
const volumeColors = computed(() => {
  if (!visibleData.value) return []
  return visibleData.value.candle.map(c => {
    const open  = c.y[0]
    const close = c.y[3]
    if (open == null || close == null) return '#94a3b8'
    return close >= open ? '#ef4444' : '#3b82f6'
  })
})

// ── 캔들스틱 시리즈 ───────────────────────────────────
const candleSeries = computed(() => {
  if (!visibleData.value) return []
  const vd  = visibleData.value
  const ind = indicators.value

  const series = [
    { name: '주가', type: 'candlestick', data: vd.candle }
  ]

  if (ind.find(i => i.key === 'ma5')?.visible) {
    series.push({
      name: 'MA5', type: 'line',
      data: vd.dates.map((d, i) => ({ x: d, y: vd.ma.ma5[i] }))
    })
  }
  if (ind.find(i => i.key === 'ma20')?.visible) {
    series.push({
      name: 'MA20', type: 'line',
      data: vd.dates.map((d, i) => ({ x: d, y: vd.ma.ma20[i] }))
    })
  }
  if (ind.find(i => i.key === 'ma60')?.visible) {
    series.push({
      name: 'MA60', type: 'line',
      data: vd.dates.map((d, i) => ({ x: d, y: vd.ma.ma60[i] }))
    })
  }
  if (ind.find(i => i.key === 'bb')?.visible) {
    series.push(
      { name: 'BB 상단', type: 'line', data: vd.dates.map((d, i) => ({ x: d, y: vd.bollinger.upper[i] })) },
      { name: 'BB 중간', type: 'line', data: vd.dates.map((d, i) => ({ x: d, y: vd.bollinger.mid[i] })) },
      { name: 'BB 하단', type: 'line', data: vd.dates.map((d, i) => ({ x: d, y: vd.bollinger.lower[i] })) }
    )
  }
  return series
})

// ── 거래량 시리즈 ─────────────────────────────────────
const volumeSeries = computed(() => {
  if (!visibleData.value) return []
  const vd = visibleData.value
  return [{
    name: '거래량',
    data: vd.dates.map((d, i) => ({ x: d, y: vd.volume[i] }))
  }]
})

// ── x축 날짜 포맷터 (TradingView 스타일) ─────────────
// 확대 시: "16일", "17일" / 축소 시: "9월", "10월" / 더 축소: "2025"
function makeXAxisFormatter(dates) {
  const total = dates.length
  // 5개 균등 간격으로 표시
  const step  = Math.max(1, Math.floor(total / 5))

  return (val, idx) => {
    // step 간격이 아닌 건 빈 문자열
    if (idx % step !== 0) return ''
    if (!val) return ''

    // val 형식에 따라 다른 포맷 적용
    // '06.22' → '6월 22일' 형태로 변환
    if (val.includes('.') && val.length <= 5) {
      // '06.22' → month=06, day=22
      const parts = val.split('.')
      const month = parseInt(parts[0], 10)
      const day   = parseInt(parts[1], 10)
      // 축소(캔들 많을수록) 시 월만, 확대(캔들 적을수록) 시 월+일
      if (total > 100) return `${month}월`
      if (total > 30)  return `${month}월`
      return `${month}월 ${day}일`
    }
    // '25.06' → '25년 6월'
    if (val.includes('.') && val.length === 5) {
      const parts = val.split('.')
      return `${parts[0]}년 ${parseInt(parts[1], 10)}월`
    }
    // '2025' → 그대로
    return val
  }
}

// ── 캔들 차트 옵션 ────────────────────────────────────
const candleOptions = computed(() => {
  const dates = visibleData.value?.dates ?? []
  const total = dates.length
  const step  = Math.max(1, Math.floor(total / 5))

  return {
    chart: {
      id: 'candle-chart',
      type: 'candlestick',
      toolbar: { show: false },       // 툴바 숨김 (TradingView 스타일)
      zoom:    { enabled: false },    // 자체 zoom off → 휠로 대체
      background: 'transparent',
      fontFamily: 'IBM Plex Mono, monospace',
      animations: { enabled: false }, // 휠 줌 시 깜빡임 방지
    },
    colors: ['#2563eb', '#f59e0b', '#10b981', '#8b5cf6', '#94a3b8', '#94a3b8', '#94a3b8'],
    stroke: { width: [1, 2, 2, 2, 1, 1, 1] },
    xaxis: {
      type: 'category',
      categories: dates,
      tickAmount: 5,
      labels: {
        rotate: 0,
        style: {
          fontFamily: 'IBM Plex Mono, monospace',
          fontSize: '11px',
          colors: '#94a3b8',
        },
        formatter: (val, idx) => {
          if (!val || idx % step !== 0) return ''
          // 캔들 개수에 따라 날짜 포맷 결정
          if (val.length === 4) return val  // '2025' 연도
          const parts = val.split('.')
          if (parts.length !== 2) return val
          const a = parseInt(parts[0], 10)
          const b = parseInt(parts[1], 10)
          // '06.22' 형식 (일봉)
          if (a <= 12 && b <= 31) {
            return total > 60 ? `${a}월` : `${a}/${b}`
          }
          // '25.06' 형식 (주봉/월봉)
          return `${a}년 ${b}월`
        }
      },
      axisBorder: { color: '#e2ecf9' },
      axisTicks:  { color: '#e2ecf9' },
      crosshairs: {
        show: true,
        stroke: { color: '#2563eb', dashArray: 3, width: 1 }
      },
    },
    yaxis: {
      opposite: true,     // y축 우측 배치 (HTS 스타일)
      tooltip:  { enabled: true },
      labels: {
        style: {
          fontFamily: 'IBM Plex Mono, monospace',
          fontSize: '11px',
          colors: '#94a3b8',
        },
        formatter: (val) => val != null ? val.toLocaleString('ko-KR') : '',
      },
    },
    tooltip: {
      shared: false,
      theme: 'light',
      style: { fontFamily: 'IBM Plex Mono, monospace', fontSize: '12px' },
    },
    plotOptions: {
      candlestick: {
        colors: {
          upward:   '#ef4444',   // 상승: 빨강 (한국식)
          downward: '#3b82f6',   // 하락: 파랑 (한국식)
        },
        wick: { useFillColor: true },
      }
    },
    legend: { show: false },
    grid: {
      borderColor: '#e2ecf9',
      xaxis: { lines: { show: false } },
      yaxis: { lines: { show: true } },
    },
  }
})

// ── 거래량 차트 옵션 ──────────────────────────────────
const volumeOptions = computed(() => {
  const dates  = visibleData.value?.dates ?? []
  const total  = dates.length
  const step   = Math.max(1, Math.floor(total / 5))
  const colors = volumeColors.value

  return {
    chart: {
      id: 'volume-chart',
      type: 'bar',
      toolbar: { show: false },
      zoom:    { enabled: false },
      background: 'transparent',
      fontFamily: 'IBM Plex Mono, monospace',
      animations: { enabled: false },
    },
    // 💡 거래량 바 색상을 캔들 상승/하락에 맞춰 개별 지정
    colors: ['#94a3b8'],
    fill: {
      type: 'solid',
      colors: colors,   // 각 바마다 빨강/파랑 적용
    },
    dataLabels: { enabled: false },
    plotOptions: {
      bar: {
        columnWidth: '80%',
        distributed: true,    // 💡 각 바에 개별 색상 적용하려면 distributed: true 필요
      }
    },
    xaxis: {
      type: 'category',
      categories: dates,
      labels: {
        rotate: 0,
        style: {
          fontFamily: 'IBM Plex Mono, monospace',
          fontSize: '10px',
          colors: '#94a3b8',
        },
        formatter: (val, idx) => {
          if (!val || idx % step !== 0) return ''
          const parts = val.split('.')
          if (parts.length !== 2) return val
          const a = parseInt(parts[0], 10)
          const b = parseInt(parts[1], 10)
          if (a <= 12 && b <= 31) {
            return total > 60 ? `${a}월` : `${a}/${b}`
          }
          return `${a}년 ${b}월`
        }
      },
      axisBorder: { color: '#e2ecf9' },
      axisTicks:  { color: '#e2ecf9' },
    },
    yaxis: {
      opposite: true,
      labels: {
        style: {
          fontFamily: 'IBM Plex Mono, monospace',
          fontSize: '10px',
          colors: '#94a3b8',
        },
        formatter: (val) => {
          if (val >= 1_000_000) return (val / 1_000_000).toFixed(1) + 'M'
          if (val >= 1_000)     return (val / 1_000).toFixed(0) + 'K'
          return val
        }
      }
    },
    legend: { show: false },
    grid: {
      borderColor: '#e2ecf9',
      xaxis: { lines: { show: false } },
    },
    tooltip: {
      theme: 'light',
      style: { fontFamily: 'IBM Plex Mono, monospace', fontSize: '11px' },
      y: {
        formatter: (val) => val != null ? val.toLocaleString('ko-KR') : '-'
      }
    },
  }
})

// ── 마우스 휠 줌 ─────────────────────────────────────
function handleWheel(e) {
  if (!chartData.value) return

  // 페이지 스크롤 막기
  e.preventDefault()
  e.stopPropagation()

  const total = chartData.value.dates.length

  // deltaY > 0: 아래 스크롤 → 축소 (캔들 늘어남)
  // deltaY < 0: 위 스크롤  → 확대 (캔들 줄어듦)
  const zoomStep = Math.max(3, Math.floor(visibleCount.value * 0.1))
  const delta    = e.deltaY > 0 ? zoomStep : -zoomStep

  visibleCount.value = Math.min(
    MAX_VISIBLE,
    Math.max(MIN_VISIBLE, visibleCount.value + delta)
  )
  // 데이터보다 많이 보려 하면 전체 데이터 수로 제한
  visibleCount.value = Math.min(visibleCount.value, total)
}

// ── API 호출 ──────────────────────────────────────────
async function fetchChart() {
  isLoading.value = true
  error.value     = null
  try {
    const res = await getStockChart(symbol, selectedInterval.value)
    chartData.value    = res.data
    visibleCount.value = 50   // interval 바뀌면 50개로 초기화
  } catch (err) {
    error.value = '차트 데이터를 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

async function fetchPriceInfo() {
  isPriceLoading.value = true
  try {
    const res = await getStockPrice(symbol)
    stockPrice.value = res.data
  } catch (err) {
    console.warn('현재가 정보를 가져오지 못했습니다.')
  } finally {
    isPriceLoading.value = false
  }
}

function changeInterval(interval) {
  selectedInterval.value = interval
}
watch(selectedInterval, fetchChart)

// 최신 캔들 데이터 (우측 패널용)
const latestCandle = computed(() => {
  if (!chartData.value?.candle) return null
  const candles = chartData.value.candle
  return candles[candles.length - 1]
})

// ── 라이프사이클 ──────────────────────────────────────
onMounted(async () => {
  watchlistStore.fetchWatchlist()
  fetchPriceInfo()
  await fetchChart()

  // chartData 로드 후 wheel 이벤트 등록
  await nextTick()
  if (chartWrapRef.value) {
    chartWrapRef.value.addEventListener('wheel', handleWheel, { passive: false })
  }
})

onUnmounted(() => {
  if (chartWrapRef.value) {
    chartWrapRef.value.removeEventListener('wheel', handleWheel)
  }
})

// ── 포맷 헬퍼 ─────────────────────────────────────────
function formatPrice(price) {
  if (price == null) return '-'
  return price.toLocaleString('ko-KR') + ' 원'
}
function formatRate(rate) {
  if (rate == null) return '-'
  return (rate > 0 ? '+' : '') + rate.toFixed(2) + '%'
}
function changeClass(change) {
  if (change > 0) return 'up'
  if (change < 0) return 'down'
  return 'flat'
}
</script>

<style scoped>
.detail-container {
  min-height: 100vh;
  background: #f0f6ff;
  color: #0f172a;
  padding: 24px;
  font-family: 'IBM Plex Mono', 'Pretendard', sans-serif;
}

/* 헤더 */
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
}
.fav-btn.active { background: #fef3c7; border-color: #f59e0b; color: #d97706; }

/* 메인 그리드 */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 20px;
  align-items: start;
}

/* 차트 섹션 */
.chart-section {
  background: white;
  border: 1px solid #e2ecf9;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
}
.chart-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
}
.period-tabs { display: flex; gap: 6px; }
.tab {
  padding: 5px 14px;
  border: 1px solid #e2ecf9;
  border-radius: 99px;
  background: #f8fafc;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  transition: all 0.15s;
}
.tab.active  { background: #2563eb; color: #fff; border-color: #2563eb; }
.tab:hover:not(.active) { background: #e2ecf9; }

.indicator-toggles { display: flex; gap: 14px; }
.toggle-label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  cursor: pointer;
  color: #475569;
}
.toggle-label input { accent-color: #2563eb; }

/* 줌 정보 */
.zoom-info {
  display: flex;
  justify-content: space-between;
  padding: 4px 2px 8px;
  font-size: 11px;
}
.zoom-count { color: #475569; font-weight: 600; }
.zoom-hint  { color: #cbd5e1; }

/* 차트 래퍼 */
.chart-zoom-wrap {
  cursor: crosshair;
  user-select: none;   /* 드래그 시 텍스트 선택 방지 */
}
.chart-wrap       { margin-bottom: 4px; }
.volume-wrap      { margin-bottom: 0; }

.chart-placeholder {
  height: 480px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-weight: 600;
}
.chart-placeholder.error { color: #ef4444; }
.disclaimer {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 16px;
  text-align: center;
}

/* 우측 패널 */
.info-section  { display: flex; flex-direction: column; gap: 16px; }
.info-card {
  background: white;
  border: 1px solid #e2ecf9;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
}
.info-card h3 {
  font-size: 0.9rem;
  font-weight: 700;
  color: #475569;
  margin: 0 0 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f1f5f9;
}
.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 9px 0;
  border-bottom: 1px dashed #f1f5f9;
  font-size: 0.88rem;
}
.info-row:last-child { border-bottom: none; }
.info-label  { color: #64748b; font-weight: 500; }
.info-value  { font-weight: 700; color: #1e293b; }
.info-value.price { font-size: 1.05rem; }
.info-loading { color: #94a3b8; font-size: 0.85rem; text-align: center; padding: 10px 0; }

.up   { color: #ef4444; }
.down { color: #3b82f6; }
.flat { color: #64748b; }

@media (max-width: 1024px) {
  .content-grid { grid-template-columns: 1fr; }
}
</style>