<!-- src/views/StockChartView.vue -->
<template>
  <div class="chart-page">

    <!-- 상단 헤더 -->
    <div class="chart-header">
      <button class="btn-back" @click="router.back()">← 뒤로</button>
      <div>
        <h1 class="chart-title">{{ symbol }}</h1>
        <p class="chart-sub">기술적 지표 차트</p>
      </div>
      <!-- 관심 종목 추가 버튼 -->
      <button
        class="btn-watchlist"
        :class="{ active: isWatched }"
        @click="handleWatchlistToggle"
      >
        {{ isWatched ? '★ 관심 종목' : '☆ 관심 종목 추가' }}
      </button>
    </div>

    <!-- 기간 선택 탭 -->
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

    <!-- 지표 토글 체크박스 -->
    <div class="indicator-toggles">
      <label v-for="ind in indicators" :key="ind.key" class="toggle-label">
        <input type="checkbox" v-model="ind.visible" />
        <span :style="{ color: ind.color }">{{ ind.label }}</span>
      </label>
    </div>

    <!-- 로딩 / 에러 / 차트 -->
    <div v-if="isLoading" class="status-box">📡 차트 데이터를 불러오는 중...</div>
    <div v-else-if="error" class="status-box error">⚠️ {{ error }}</div>

    <template v-else-if="chartData">
      <!-- 메인 캔들 + 이동평균 + 볼린저 밴드 차트 -->
      <div class="chart-wrap">
        <apexchart
          type="candlestick"
          height="420"
          :options="candleOptions"
          :series="candleSeries"
        />
      </div>

      <!-- 거래량 차트 -->
      <div class="chart-wrap">
        <apexchart
          type="bar"
          height="150"
          :options="volumeOptions"
          :series="volumeSeries"
        />
      </div>
    </template>

    <!-- 투자 주의 문구 -->
    <p class="disclaimer">
      ⚠️ 이 차트는 참고용 정보이며, 투자 권유가 아닙니다. 투자에는 항상 위험이 따릅니다.
    </p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import VueApexCharts from 'vue3-apexcharts'
import { getStockChart } from '@/api/stocks'
import { useWatchlistStore } from '@/stores/watchlist'

// ApexCharts 컴포넌트를 'apexchart' 이름으로 등록
const apexchart = VueApexCharts

const route  = useRoute()
const router = useRouter()
const watchlistStore = useWatchlistStore()

// URL 파라미터에서 종목 심볼 가져오기
// 예: /stocks/chart/AAPL → symbol = 'AAPL'
const symbol = route.params.symbol

// ── 상태 ─────────────────────────────────────────────
const chartData      = ref(null)   // 백엔드에서 받은 차트 원본 데이터
const isLoading      = ref(false)
const error          = ref(null)
const selectedPeriod = ref('3mo') // 현재 선택된 기간

// ── 기간 탭 목록 ──────────────────────────────────────
const periods = [
  { label: '1개월', value: '1mo' },
  { label: '3개월', value: '3mo' },
  { label: '6개월', value: '6mo' },
  { label: '1년',   value: '1y'  },
]

// ── 지표 토글 목록 ────────────────────────────────────
// visible을 reactive하게 관리 → 체크박스 on/off 시 차트 즉시 반영
const indicators = ref([
  { key: 'ma5',    label: 'MA5',       color: '#f59e0b', visible: true  },
  { key: 'ma20',   label: 'MA20',      color: '#10b981', visible: true  },
  { key: 'ma60',   label: 'MA60',      color: '#8b5cf6', visible: false },
  { key: 'bb',     label: '볼린저밴드', color: '#94a3b8', visible: false },
])

// ── 관심 종목 여부 ────────────────────────────────────
const isWatched = computed(() =>
  watchlistStore.watchedSymbols.includes(symbol)
)

async function handleWatchlistToggle() {
  if (isWatched.value) {
    // 이미 관심 종목이면 → 관심 종목 페이지로 이동
    router.push({ name: 'stock-watchlist' })
  } else {
    // 아직 추가 안 됐으면 → 추가 요청
    // name, market은 간단히 symbol로 채움 (검색 기능 연동 전 임시)
    await watchlistStore.addToWatchlist({
      symbol,
      name:   symbol,
      market: 'UNKNOWN',
    })
  }
}

// ── 차트 데이터 로드 ──────────────────────────────────
async function fetchChart() {
  isLoading.value = true
  error.value     = null
  try {
    const res   = await getStockChart(symbol, selectedPeriod.value)
    chartData.value = res.data
  } catch (err) {
    error.value = '차트 데이터를 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

function changePeriod(period) {
  selectedPeriod.value = period
  // selectedPeriod가 바뀌면 watch가 감지해서 자동으로 fetchChart 호출
}

// selectedPeriod가 바뀔 때마다 차트 다시 로드
watch(selectedPeriod, fetchChart)

// ── ApexCharts 시리즈(데이터) 계산 ───────────────────
// computed로 만들면 chartData나 indicators가 바뀔 때 자동으로 재계산됨

const candleSeries = computed(() => {
  if (!chartData.value) return []

  const series = [
    // 캔들스틱 시리즈 (항상 표시)
    {
      name: '주가',
      type: 'candlestick',
      data: chartData.value.candle,
    }
  ]

  // 체크박스 상태에 따라 지표 시리즈 추가
  const ind = indicators.value

  if (ind.find(i => i.key === 'ma5')?.visible) {
    series.push({
      name: 'MA5', type: 'line',
      data: chartData.value.dates.map((d, i) => ({
        x: d, y: chartData.value.ma.ma5[i]
      }))
    })
  }
  if (ind.find(i => i.key === 'ma20')?.visible) {
    series.push({
      name: 'MA20', type: 'line',
      data: chartData.value.dates.map((d, i) => ({
        x: d, y: chartData.value.ma.ma20[i]
      }))
    })
  }
  if (ind.find(i => i.key === 'ma60')?.visible) {
    series.push({
      name: 'MA60', type: 'line',
      data: chartData.value.dates.map((d, i) => ({
        x: d, y: chartData.value.ma.ma60[i]
      }))
    })
  }
  if (ind.find(i => i.key === 'bb')?.visible) {
    series.push(
      {
        name: 'BB 상단', type: 'line',
        data: chartData.value.dates.map((d, i) => ({
          x: d, y: chartData.value.bollinger.upper[i]
        }))
      },
      {
        name: 'BB 중간', type: 'line',
        data: chartData.value.dates.map((d, i) => ({
          x: d, y: chartData.value.bollinger.mid[i]
        }))
      },
      {
        name: 'BB 하단', type: 'line',
        data: chartData.value.dates.map((d, i) => ({
          x: d, y: chartData.value.bollinger.lower[i]
        }))
      }
    )
  }

  return series
})

// ── ApexCharts 옵션(설정) ─────────────────────────────
const candleOptions = computed(() => ({
  chart: {
    id: 'candle-chart',
    type: 'candlestick',
    toolbar: { show: true },
    zoom: { enabled: true },
  },
  // 지표별 색상 지정
  colors: ['#2563eb', '#f59e0b', '#10b981', '#8b5cf6', '#94a3b8', '#94a3b8', '#94a3b8'],
  stroke: {
    width: [1, 2, 2, 2, 1, 1, 1],  // 캔들은 얇게, 이동평균선은 2px
  },
  xaxis: {
    type: 'category',
    labels: { rotate: -45, style: { fontSize: '11px' } },
  },
  yaxis: {
    tooltip: { enabled: true },
    labels: {
      // 숫자를 보기 좋게 포맷팅 (예: 150.12)
      formatter: (val) => val != null ? val.toFixed(2) : '',
    }
  },
  tooltip: {
    shared: true,  // 여러 시리즈의 툴팁을 한 번에 표시
    // 캔들스틱 툴팁 커스터마이징
    custom: undefined,
  },
  plotOptions: {
    candlestick: {
      colors: {
        upward:   '#ef4444',  // 상승 캔들: 빨간색 (한국식)
        downward: '#2563eb',  // 하락 캔들: 파란색 (한국식)
      }
    }
  },
  legend: { show: true, position: 'top' },
}))

// 거래량 시리즈
const volumeSeries = computed(() => {
  if (!chartData.value) return []
  return [{
    name: '거래량',
    data: chartData.value.dates.map((d, i) => ({
      x: d,
      y: chartData.value.volume[i]
    }))
  }]
})

// 거래량 차트 옵션
const volumeOptions = computed(() => ({
  chart: {
    id: 'volume-chart',
    type: 'bar',
    toolbar: { show: false },
    // 메인 차트와 x축 동기화
    brush: { target: 'candle-chart', enabled: true },
  },
  colors: ['#94a3b8'],
  xaxis: { type: 'category', labels: { show: false } },
  yaxis: {
    labels: {
      // 거래량 단위 축약 (예: 1,200,000 → 1.2M)
      formatter: (val) => {
        if (val >= 1_000_000) return (val / 1_000_000).toFixed(1) + 'M'
        if (val >= 1_000)     return (val / 1_000).toFixed(0) + 'K'
        return val
      }
    }
  },
  dataLabels: { enabled: false },
  plotOptions: { bar: { columnWidth: '80%' } },
}))

// ── 마운트 시 초기 데이터 로드 ───────────────────────
onMounted(() => {
  watchlistStore.fetchWatchlist()  // 관심 종목 여부 확인용
  fetchChart()
})
</script>

<style scoped>
.chart-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 28px 20px;
}
.chart-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}
.btn-back {
  padding: 8px 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  font-size: 14px;
}
.chart-title { font-size: 26px; font-weight: 700; margin: 0; }
.chart-sub   { font-size: 13px; color: #888; margin: 2px 0 0; }
.btn-watchlist {
  margin-left: auto;
  padding: 8px 18px;
  border: 1px solid #2563eb;
  border-radius: 8px;
  background: #fff;
  color: #2563eb;
  cursor: pointer;
  font-weight: 600;
}
.btn-watchlist.active {
  background: #2563eb;
  color: #fff;
}
.period-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 14px;
}
.tab {
  padding: 6px 16px;
  border: 1px solid #ddd;
  border-radius: 99px;
  background: #fff;
  cursor: pointer;
  font-size: 13px;
}
.tab.active {
  background: #2563eb;
  color: #fff;
  border-color: #2563eb;
}
.indicator-toggles {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.toggle-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  cursor: pointer;
}
.chart-wrap {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.07);
  margin-bottom: 16px;
}
.status-box {
  text-align: center;
  padding: 80px;
  color: #aaa;
  font-size: 15px;
}
.status-box.error { color: #ef4444; }
.disclaimer {
  font-size: 12px;
  color: #aaa;
  margin-top: 24px;
  text-align: center;
}
</style>