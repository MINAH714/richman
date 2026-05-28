<template>
  <div class="detail-wrapper">
    <header class="detail-header">
      <button class="back-btn" @click="router.push('/crypto')">
        <span class="back-icon">←</span> BACK TO MARKET
      </button>
    </header>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>코인 상세 정보를 불러오는 중입니다...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <span class="error-icon">⚠</span>
      <p>{{ error }}</p>
      <button @click="fetchCoinDetail" class="retry-btn">재시도</button>
    </div>

    <div v-else class="content-container">
      <section class="top-info-card">
        <div class="title-row">
          <div class="name-group">
            <h1 class="kr-name">{{ coin?.korean_name }}</h1>
            <span class="en-name">{{ coin?.english_name }}</span>
            <span class="market-badge">{{ coin?.market }}</span>
          </div>
          <button class="fav-btn" @click="toggleFavorite">
            <span class="fav-star" :class="{ active: isFavorite }">
              {{ isFavorite ? '★' : '☆' }}
            </span>
          </button>
        </div>

        <div class="price-row">
          <div class="current-price" :class="colorClass">
            {{ formatPrice(coin?.trade_price) }} <span class="unit">KRW</span>
          </div>
          <div class="change-info" :class="colorClass">
            <span class="change-rate">{{ changeSign }}{{ formatChangeRate(coin?.signed_change_rate) }}</span>
            <span class="change-price">({{ changeSign }}{{ formatPrice(Math.abs(coin?.signed_change_price || 0)) }})</span>
          </div>
        </div>

        <div class="stats-grid">
          <div class="stat-box">
            <span class="stat-label">고가(52주)</span>
            <span class="stat-value text-red">{{ formatPrice(coin?.highest_52_week_price) }}</span>
            <span class="stat-date">{{ coin?.highest_52_week_date }}</span>
          </div>
          <div class="stat-box">
            <span class="stat-label">저가(52주)</span>
            <span class="stat-value text-blue">{{ formatPrice(coin?.lowest_52_week_price) }}</span>
            <span class="stat-date">{{ coin?.lowest_52_week_date }}</span>
          </div>
          <div class="stat-box">
            <span class="stat-label">거래대금(24H)</span>
            <span class="stat-value">{{ formatVolume(coin?.acc_trade_price_24h) }}</span>
          </div>
          <div class="stat-box">
            <span class="stat-label">거래량(24H)</span>
            <span class="stat-value">{{ formatPrice(coin?.acc_trade_volume_24h) }} {{ coin?.market?.split('-')[1] }}</span>
          </div>
        </div>
      </section>

      <section class="chart-card">
        <h2 class="section-title">일봉 차트</h2>
        <div class="chart-container">
          <apexchart 
            type="candlestick" 
            height="400" 
            :options="chartOptions" 
            :series="chartSeries"
          ></apexchart>
        </div>
      </section>

      <div class="future-features-grid">
        <section class="future-card">
          <div class="card-header">
            <span class="icon">📰</span>
            <h3>Social Buzz (예정)</h3>
          </div>
          <p>네이버 뉴스 API 연동 및 주요 키워드 추출을 통한 소셜 데이터 분석 요약이 제공될 예정입니다.</p>
        </section>

        <section class="future-card">
          <div class="card-header">
            <span class="icon">🤖</span>
            <h3>코인 감정 지표 (예정)</h3>
          </div>
          <p>GPT 기반 감성 분석을 통해 현재 시장의 투자 심리(공포/탐욕 지수 등)가 제공될 예정입니다.</p>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { cryptoAPI } from '@/api/crypto'
import VueApexCharts from 'vue3-apexcharts'

// 컴포넌트 등록
const apexchart = VueApexCharts

const route = useRoute()
const router = useRouter()
const market = route.params.market

// 상태 관리
const isLoading = ref(true)
const error = ref(null)
const coin = ref(null)
const isFavorite = ref(false)

// 차트 데이터 (OHLC: Open, High, Low, Close)
const chartSeries = ref([{
  name: '시세',
  data: []
}])

// 차트 옵션 설정
const chartOptions = ref({
  chart: {
    type: 'candlestick',
    fontFamily: "'IBM Plex Mono', 'Noto Sans KR', sans-serif",
    toolbar: { show: false },
    background: 'transparent'
  },
  plotOptions: {
    candlestick: {
      colors: {
        upward: '#059669',   // 글로벌 표준 상승 (Green)
        downward: '#dc2626'  // 글로벌 표준 하락 (Red)
      },
      wick: { useDataColors: true }
    }
  },
  xaxis: {
    type: 'datetime',
    labels: {
      style: { colors: '#94a3b8', fontSize: '11px' },
      datetimeUTC: false
    },
    axisBorder: { color: '#e2ecf9' },
    axisTicks: { color: '#e2ecf9' }
  },
  yaxis: {
    tooltip: { enabled: true },
    labels: {
      style: { colors: '#94a3b8', fontSize: '11px' },
      formatter: (value) => value.toLocaleString('ko-KR')
    }
  },
  grid: {
    borderColor: '#e2ecf9',
    strokeDashArray: 4,
    xaxis: { lines: { show: true } },
    yaxis: { lines: { show: true } },
  },
  tooltip: {
    theme: 'light',
    x: { format: 'yyyy-MM-dd HH:mm' }
  }
})

// 계산 프로퍼티
const colorClass = computed(() => {
  if (!coin.value) return ''
  return coin.value.signed_change_rate > 0 ? 'text-green' : 
         coin.value.signed_change_rate < 0 ? 'text-red' : 'text-muted'
})

const changeSign = computed(() => {
  if (!coin.value) return ''
  return coin.value.signed_change_rate > 0 ? '+' : ''
})

// API 호출
const fetchCoinDetail = async () => {
  try {
    isLoading.value = true
    error.value = null
    
    // API 호출 (Ticker 및 캔들 데이터)
    const response = await cryptoAPI.getCoinDetail(market)
    
    // 백엔드 응답 구조에 맞게 매핑
    // 가정: response.data가 { ticker: {}, candles: [] } 형태이거나 단일 객체/배열
    const data = response.data
    
    // 1. Ticker 데이터 매핑 (응답이 배열인 경우와 객체인 경우 모두 처리)
    coin.value = Array.isArray(data) ? data[0] : (data.ticker || data)

    // 2. 캔들 차트 데이터 매핑
    // 백엔드에서 candles 배열을 준다고 가정. (없으면 임시 빈 배열)
    const candles = data.candles || []
    chartSeries.value = [{
      name: '시세',
      data: candles.map(c => ({
        x: new Date(c.candle_date_time_kst || c.timestamp).getTime(),
        y: [c.opening_price, c.high_price, c.low_price, c.trade_price]
      }))
    }]

    // TODO: 즐겨찾기 상태 조회 로직 추가 (cryptoAPI.getFavorites() 연동)
    
  } catch (err) {
    error.value = '코인 상세 데이터를 불러오지 못했습니다.'
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

const toggleFavorite = () => {
  // TODO: cryptoAPI.addFavorite / removeFavorite 연동
  isFavorite.value = !isFavorite.value
}

// 유틸 함수
const formatPrice = (price) => {
  if (!price) return '0'
  if (price >= 100) return Number(price).toLocaleString('ko-KR', { maximumFractionDigits: 0 })
  return Number(price).toLocaleString('ko-KR', { maximumFractionDigits: 4 })
}

const formatChangeRate = (rate) => {
  if (!rate) return '0.00%'
  return (rate * 100).toFixed(2) + '%'
}

const formatVolume = (vol) => {
  if (!vol) return '-'
  const v = Number(vol)
  if (v >= 1_000_000_000_000) return (v / 1_000_000_000_000).toFixed(2) + '조'
  if (v >= 100_000_000) return (v / 100_000_000).toFixed(0) + '억'
  if (v >= 10_000) return (v / 10_000).toFixed(0) + '만'
  return v.toLocaleString('ko-KR')
}

onMounted(() => {
  fetchCoinDetail()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Noto+Sans+KR:wght@400;500;700&display=swap');

:root {
  --bg: #f0f6ff;
  --bg-card: #ffffff;
  --border: #e2ecf9;
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #94a3b8;
  --green: #059669;
  --red: #dc2626;
  --blue: #2563eb;
  --font-mono: 'IBM Plex Mono', monospace;
  --font-kr: 'Noto Sans KR', sans-serif;
}

.detail-wrapper {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text-primary);
  font-family: var(--font-kr);
  padding-bottom: 60px;
}

/* 유틸 컬러 */
.text-green { color: var(--green); }
.text-red { color: var(--red); }
.text-blue { color: var(--blue); }
.text-muted { color: var(--text-muted); }

/* 헤더 */
.detail-header {
  padding: 16px 28px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.back-btn {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.1em;
  color: var(--text-secondary);
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: color 0.2s;
}
.back-btn:hover { color: var(--blue); }
.back-icon { font-size: 16px; }

/* 컨텐츠 컨테이너 */
.content-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 카드 공통 */
.top-info-card, .chart-card, .future-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

/* 상단 정보 영역 */
.title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}
.name-group {
  display: flex;
  align-items: baseline;
  gap: 12px;
}
.kr-name {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
}
.en-name {
  font-size: 14px;
  color: var(--text-muted);
}
.market-badge {
  font-family: var(--font-mono);
  font-size: 11px;
  background: var(--bg);
  padding: 4px 8px;
  border-radius: 4px;
  color: var(--text-secondary);
  border: 1px solid var(--border);
}

.fav-btn {
  background: none;
  border: none;
  cursor: pointer;
}
.fav-star {
  font-size: 24px;
  color: var(--border);
  transition: all 0.2s;
}
.fav-star.active { color: #d97706; }

.price-row {
  margin-bottom: 24px;
}
.current-price {
  font-family: var(--font-mono);
  font-size: 36px;
  font-weight: 600;
  line-height: 1.2;
}
.unit {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-secondary);
}
.change-info {
  font-family: var(--font-mono);
  font-size: 16px;
  font-weight: 500;
  margin-top: 4px;
}

/* 통계 그리드 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  padding-top: 24px;
  border-top: 1px solid var(--border);
}
.stat-box {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.stat-label {
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 0.05em;
}
.stat-value {
  font-family: var(--font-mono);
  font-size: 15px;
  font-weight: 600;
}
.stat-date {
  font-size: 10px;
  color: var(--text-muted);
}

/* 차트 영역 */
.section-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px 0;
  color: var(--text-primary);
}
.chart-container {
  min-height: 400px;
}

/* 예정 기능 영역 */
.future-features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.card-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--blue);
  margin: 0;
}
.icon { font-size: 20px; }
.future-card p {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0;
}

/* 상태 표시 */
.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 20px;
  color: var(--text-muted);
  font-size: 14px;
}
.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid var(--border);
  border-top-color: var(--blue);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
.error-icon {
  font-size: 32px;
  color: var(--red);
  margin-bottom: 16px;
}
.retry-btn {
  margin-top: 16px;
  padding: 8px 24px;
  border: 1px solid var(--red);
  color: var(--red);
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  font-family: var(--font-mono);
}
.retry-btn:hover { background: rgba(220, 38, 38, 0.05); }
</style>