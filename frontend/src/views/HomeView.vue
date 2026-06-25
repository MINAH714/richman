// frontend/src/views/HomeView.vue
<template>
  <div class="home-wrapper" :class="{ 'is-scrolled': hasScrolled }">게시판
    
    <!-- 🌟 1. 완전 메인 (Cover Hero with Video Background) -->
    <section 
      class="grand-hero" 
      ref="grandHeroRef" 
      @wheel.prevent="handleHeroScroll"
    >
      <!-- 동적 모션 그래픽 배경 (로딩 실패/403 대비 폴백 그라데이션) -->
      <div class="video-fallback"></div>
      
      <!-- 💡 403 에러 해결: 외부 CDN 핫링킹 차단이 없는 안정적인 소스로 교체 -->
      <!-- 실무 배포 시에는 영상을 /public/videos/main-bg.mp4 에 저장하고 src="/videos/main-bg.mp4" 로 사용하는 것을 권장합니다. -->
      <video class="video-bg" autoplay loop muted playsinline>
        <source src="/main-bg.mp4" type="video/mp4" />
      </video>
      <div class="video-overlay"></div>

      <div class="grand-content">
        <p class="grand-eyebrow">SMART FINANCIAL PLATFORM</p>
        <h1 class="grand-title">
          당신의 모든 자산,<br/>
          <span class="text-gradient">완벽한 하나의 시야로.</span>
        </h1>
        <p class="grand-desc">
          주식, 크립토, 예적금까지. AI가 분석하는 나만의 맞춤형 금융 인사이트를 지금 바로 경험하세요.
        </p>
      </div>

      <!-- 스크롤 유도 애니메이션 -->
      <div class="scroll-indicator" @click="scrollToDashboard">
        <div class="mouse">
          <div class="wheel"></div>
        </div>
        <span class="scroll-text">SCROLL DOWN</span>
      </div>
    </section>

    <!-- 📊 2. 대시보드 (원래 메인 페이지) -->
    <div class="dashboard-container" ref="dashboardRef">
      <div class="home">
        
        <!-- Hero (요약 카드들) -->
        <section class="hero-section">
          <div class="section-inner hero-grid">
            <div class="hero-text">
              <p class="eyebrow">DASHBOARD</p>
              <h2 class="hero-title">내 자산 한눈에 보기</h2>
              <p class="hero-desc">
                소비 · 주식 · 크립토 데이터를 통합 분석하고<br>
                AI가 맞춤 인사이트를 제공합니다
              </p>
              <div class="hero-btns">
                <router-link to="/finlife" class="btn btn-primary">
                  <i class="ti ti-building-bank" aria-hidden="true"></i> 예적금
                </router-link>
                <router-link to="/stocks/watchlist" class="btn btn-primary">
                  <i class="ti ti-chart-candle" aria-hidden="true"></i> 주식/현물
                </router-link>
                <router-link to="/crypto" class="btn btn-primary">
                  <i class="ti ti-coin" aria-hidden="true"></i> 크립토
                </router-link>
                <router-link to="/chat" class="btn btn-outline">
                  <i class="ti ti-robot" aria-hidden="true"></i> AI 비서 시작
                </router-link>
              </div>
            </div>

            <div class="hero-cards">
              <div class="hero-cards-col">
                <div class="hero-graph-card" style="cursor:pointer" @click="$router.push('/stocks/chart/005930.KS')">
                  <p class="graph-label">삼성전자 (005930.KS)</p>
                  <p class="graph-value">
                    <span v-if="samsungPrice">{{ samsungPrice.toLocaleString('ko-KR') }}원</span>
                    <span v-else class="graph-loading">로딩 중...</span>
                    <span v-if="samsungChangeRate != null" class="graph-rate" :class="samsungChangeRate >= 0 ? 'up' : 'down'">
                      {{ samsungChangeRate >= 0 ? '+' : '' }}{{ samsungChangeRate }}%
                    </span>
                  </p>
                  <svg viewBox="0 0 280 90" class="graph-svg" role="img" aria-label="삼성전자 주가 추이">
                    <polyline :points="samsungChartPoints" fill="none" stroke="#ef4444" stroke-width="2.5" />
                    <polygon :points="samsungChartAreaPoints" fill="#fef2f2" opacity="0.6" />
                  </svg>
                </div>

                <div class="hero-graph-card" style="cursor:pointer" @click="$router.push('/crypto/KRW-BTC')">
                  <p class="graph-label">비트코인 (BTC)</p>
                  <p class="graph-value">
                    {{ formatPrice(btcTicker?.trade_price) }}
                    <span class="graph-rate" :class="changeClass(btcTicker?.change)">
                      {{ formatRate(btcTicker?.change_rate, btcTicker?.change) }}
                    </span>
                  </p>
                  <svg viewBox="0 0 280 90" class="graph-svg" role="img" aria-label="비트코인 30일 가격 추이">
                    <polyline :points="chartPoints" fill="none" stroke="#378ADD" stroke-width="2.5" />
                    <polygon :points="chartAreaPoints" fill="#E6F1FB" opacity="0.6" />
                  </svg>
                </div>
              </div>

              <div class="hero-cards-col">
                <div class="hero-graph-card forex-card">
                  <div class="forex-header">
                    <p class="graph-label">실시간 주요 환율 (KRW)</p>
                    <span class="live-dot pulse">LIVE</span>
                  </div>
                  <div class="forex-list">
                    <div v-for="fx in forexRates" :key="fx.id" class="forex-item">
                      <div class="forex-name-group">
                        <span class="forex-flag" aria-hidden="true">{{ fx.flag }}</span>
                        <span class="forex-name">{{ fx.name }}</span>
                      </div>
                      <div class="forex-price-group">
                        <span class="forex-price">
                          {{ fx.price != null ? fx.price.toLocaleString('ko-KR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '-' }}
                        </span>
                        <span class="forex-rate" :class="fx.change_type === 'RISE' ? 'up' : fx.change_type === 'FALL' ? 'down' : 'flat'">
                          {{ fx.change_rate != null ? (fx.change_rate > 0 ? '+' : '') + fx.change_rate + '%' : '-' }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 주식 시세 -->
        <section class="preview-section">
          <div class="section-inner">
            <div class="section-header">
              <h2 class="section-title">📈 주식 시세</h2>
              <span class="live-dot">LIVE</span>
              <router-link to="/stocks/watchlist" class="section-link">전체 보기 →</router-link>
            </div>
            <div v-if="isStockLoading" class="preview-grid">
              <div class="metric-card skeleton" v-for="n in 4" :key="n" />
            </div>
            <div v-else class="preview-grid">
              <router-link v-for="stock in stockPrices" :key="stock.symbol" :to="`/stocks/chart/${stock.symbol}`" class="metric-card">
                <p class="metric-label">{{ stock.name }}</p>
                <p class="metric-value">
                  {{ stock.current_price != null ? stock.current_price.toLocaleString('ko-KR') : '-' }}
                  <span class="metric-unit">{{ stock.symbol.endsWith('.KS') ? '원' : 'USD' }}</span>
                </p>
                <p class="metric-rate" :class="stock.change_type === 'RISE' ? 'up' : stock.change_type === 'FALL' ? 'down' : 'flat'">
                  {{ stock.change_rate != null ? (stock.change_rate >= 0 ? '+' : '') + stock.change_rate + '%' : '-' }}
                </p>
              </router-link>
            </div>
          </div>
        </section>

        <!-- 크립토 시세 -->
        <section class="preview-section">
          <div class="section-inner">
            <div class="section-header">
              <h2 class="section-title">🪙 크립토 시세</h2>
              <span class="live-dot">LIVE</span>
              <router-link to="/crypto" class="section-link">전체 보기 →</router-link>
            </div>
            <div v-if="isLoading" class="preview-grid">
              <div class="metric-card skeleton" v-for="n in 4" :key="n" />
            </div>
            <div v-else class="preview-grid">
              <router-link v-for="coin in topCoins" :key="coin.market" :to="`/crypto/${coin.market}`" class="metric-card">
                <p class="metric-label">{{ coin.coin_symbol }}</p>
                <p class="metric-value">{{ formatPrice(coin.trade_price) }}</p>
                <p class="metric-rate" :class="changeClass(coin.change)">
                  {{ formatRate(coin.change_rate, coin.change) }}
                </p>
              </router-link>
              <!-- AI 챗봇 유도 -->
              <router-link to="/chat" class="metric-card ai-card">
                <p class="metric-label">AI 금융 비서</p>
                <p class="metric-value">포트폴리오 분석</p>
                <p class="metric-rate up">지금 상담하기 →</p>
              </router-link>
            </div>
          </div>
        </section>

        <!-- 기능 바로가기 -->
        <section class="feature-section">
          <div class="section-inner">
            <h2 class="section-title center">기능 바로가기</h2>
            <div class="feature-grid">
              <router-link to="/finlife" class="feature-card feature-card--active">
                <i class="ti ti-building-bank feature-icon--active" aria-hidden="true"></i>
                <p class="feature-name">예적금 랭킹</p>
                <p class="feature-status">최고 금리 찾기</p>
                <span class="feature-btn feature-btn--primary">바로가기 →</span>
              </router-link>
              <router-link to="/stocks/watchlist" class="feature-card feature-card--active">
                <i class="ti ti-chart-line feature-icon--active" aria-hidden="true"></i>
                <p class="feature-name">주식 및 현물</p>
                <p class="feature-status">실시간 시세 차트</p>
                <span class="feature-btn feature-btn--primary">바로가기 →</span>
              </router-link>
              <router-link to="/youtube" class="feature-card feature-card--active">
                <i class="ti ti-brand-youtube feature-icon--active" aria-hidden="true"></i>
                <p class="feature-name">관심 영상</p>
                <p class="feature-status">유튜브 트렌드 분석</p>
                <span class="feature-btn feature-btn--primary">바로가기 →</span>
              </router-link>
              <router-link to="/crypto/buzz" class="feature-card feature-card--active">
                <i class="ti ti-flame feature-icon--active" aria-hidden="true"></i>
                <p class="feature-name">크립토 버즈</p>
                <p class="feature-status feature-status--live">실시간 감성분석</p>
                <span class="feature-btn feature-btn--primary">바로가기 →</span>
              </router-link>
              <router-link to="/chat" class="feature-card feature-card--active">
                <i class="ti ti-message-chatbot feature-icon--active" aria-hidden="true"></i>
                <p class="feature-name">AI 맞춤 추천</p>
                <p class="feature-status">나만의 금융 비서</p>
                <span class="feature-btn feature-btn--primary">바로가기 →</span>
              </router-link>
              <router-link to="/bank-map" class="feature-card feature-card--active">
                <i class="ti ti-map-pin feature-icon--active" aria-hidden="true"></i>
                <p class="feature-name">주변 은행 검색</p>
                <p class="feature-status">내 위치 기반 경로안내</p>
                <span class="feature-btn feature-btn--primary">바로가기 →</span>
              </router-link>
            </div>
          </div>
        </section>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { cryptoAPI } from '@/api/crypto'
import { getStockChart, getStockPrice } from '@/api/stocks'

// ── 스크롤 및 화면 전환 로직 ──
const dashboardRef = ref(null)
const grandHeroRef = ref(null)
const hasScrolled = ref(false)
let scrollLock = false

function scrollToDashboard() {
  dashboardRef.value?.scrollIntoView({ behavior: 'smooth' })
  hasScrolled.value = true
}

function handleHeroScroll(e) {
  if (e.deltaY > 0 && !scrollLock) {
    scrollLock = true
    scrollToDashboard()
    setTimeout(() => { scrollLock = false }, 1000)
  }
}

function checkScroll() {
  hasScrolled.value = window.scrollY > 100
}

// ── 주식 데이터 로직 ──
const STOCK_TICKERS = [
  { symbol: '005930.KS', name: '삼성전자' },
  { symbol: '000660.KS', name: 'SK하이닉스' },
  { symbol: 'AAPL',      name: 'Apple' },
  { symbol: 'NVDA',      name: 'NVIDIA' },
]

const stockPrices = ref([])
const isStockLoading = ref(true)

async function loadStockPrices() {
  try {
    const results = await Promise.allSettled(STOCK_TICKERS.map(t => getStockPrice(t.symbol)))
    const fresh = results.map((result, i) => {
      const ticker = STOCK_TICKERS[i]
      if (result.status === 'fulfilled') {
        const data = result.value.data
        return { symbol: ticker.symbol, name: ticker.name, current_price: data.current_price, change_rate: data.change_rate, change_type: data.change_type }
      }
      return { symbol: ticker.symbol, name: ticker.name, current_price: null, change_rate: null, change_type: 'EVEN' }
    })
    
    if (stockPrices.value.length === 0) {
      stockPrices.value = fresh
    } else {
      stockPrices.value.forEach((item, i) => {
        item.current_price = fresh[i]?.current_price ?? item.current_price
        item.change_rate = fresh[i]?.change_rate ?? item.change_rate
        item.change_type = fresh[i]?.change_type ?? item.change_type
      })
    }
  } catch (e) {
    console.warn('주식 시세 로드 실패:', e)
  } finally {
    isStockLoading.value = false
  }
}

// ── 환율 데이터 로직 ──
const FOREX_TICKERS = [
  { symbol: 'KRW=X', name: 'USD', id: 'USD', flag: '🇺🇸', multiplier: 1 },
  { symbol: 'EURKRW=X', name: 'EUR', id: 'EUR', flag: '🇪🇺', multiplier: 1 },
  { symbol: 'JPYKRW=X', name: 'JPY(100)', id: 'JPY', flag: '🇯🇵', multiplier: 100 },
  { symbol: 'CNYKRW=X', name: 'CNY', id: 'CNY', flag: '🇨🇳', multiplier: 1 },
]

const forexRates = ref(FOREX_TICKERS.map(t => ({ ...t, price: null, change_rate: null, change_type: 'EVEN' })))

async function loadForexRates() {
  try {
    const results = await Promise.allSettled(FOREX_TICKERS.map(t => getStockPrice(t.symbol)))
    results.forEach((result, i) => {
      if (result.status === 'fulfilled' && result.value.data) {
        const data = result.value.data
        let price = data.current_price
        if (price != null) price *= FOREX_TICKERS[i].multiplier
        forexRates.value[i].price = price
        forexRates.value[i].change_rate = data.change_rate
        forexRates.value[i].change_type = data.change_type
      }
    })
  } catch (e) { console.warn('환율 데이터 로드 실패:', e) }
}

// ── 크립토 데이터 로직 ──
const allCoins = ref([])
const isLoading = ref(true)
const candles = ref([])

const topCoins = computed(() => [...allCoins.value].sort((a, b) => (b.acc_trade_price_24h ?? 0) - (a.acc_trade_price_24h ?? 0)).slice(0, 3))
const btcTicker = computed(() => allCoins.value.find(c => c.market === 'KRW-BTC'))

const samsungPrices = ref([])
const samsungPrice = ref(null)
const samsungChangeRate = ref(null)

async function loadSamsungChart() {
  try {
    const res = await getStockChart('005930.KS', '1d')
    const data = res.data
    if (!data || !data.candle || data.candle.length === 0) return
    const candles30 = data.candle.slice(-30)
    samsungPrices.value = candles30.map(c => c.y[3]).filter(v => v != null)
    const latest = samsungPrices.value[samsungPrices.value.length - 1]
    const prev = samsungPrices.value[samsungPrices.value.length - 2]
    samsungPrice.value = latest
    if (latest && prev && prev !== 0) {
      samsungChangeRate.value = parseFloat(((latest - prev) / prev * 100).toFixed(2))
    }
  } catch (e) { console.warn('삼성전자 차트 로드 실패:', e) }
}

const samsungChartPoints = computed(() => {
  const prices = samsungPrices.value
  if (!prices || prices.length < 2) return '0,70 280,70'
  const min = Math.min(...prices)
  const max = Math.max(...prices)
  const range = max - min || 1
  const stepX = 280 / (prices.length - 1)
  return prices.map((p, i) => `${(i * stepX).toFixed(1)},${(90 - ((p - min) / range) * 80 - 5).toFixed(1)}`).join(' ')
})
const samsungChartAreaPoints = computed(() => `0,90 ${samsungChartPoints.value} 280,90`)

const chartPoints = computed(() => {
  if (!candles.value.length) return '0,70 280,70'
  const prices = candles.value.map(c => c.trade_price).reverse()
  const min = Math.min(...prices)
  const max = Math.max(...prices)
  const range = max - min || 1
  const stepX = 280 / (prices.length - 1)
  return prices.map((p, i) => `${(i * stepX).toFixed(1)},${(90 - ((p - min) / range) * 80 - 5).toFixed(1)}`).join(' ')
})
const chartAreaPoints = computed(() => `0,90 ${chartPoints.value} 280,90`)

async function loadCoins() {
  try {
    const { data } = await cryptoAPI.getCoins()
    allCoins.value = data
  } catch (e) { console.error('코인 로드 실패:', e) } 
  finally { isLoading.value = false }
}

async function loadBtcCandles() {
  try {
    const { data } = await cryptoAPI.getCoinDetail('KRW-BTC')
    candles.value = data.candles ?? []
  } catch (e) { console.error('캔들 로드 실패:', e) }
}

let timer = null
onMounted(() => {
  window.addEventListener('scroll', checkScroll)
  loadCoins()
  loadBtcCandles()
  loadSamsungChart()
  loadStockPrices()
  loadForexRates()
  timer = setInterval(() => { loadCoins(); loadForexRates() }, 10_000)
})

onUnmounted(() => {
  window.removeEventListener('scroll', checkScroll)
  clearInterval(timer)
})

function formatPrice(price) {
  if (price == null) return '-'
  return price >= 100 ? price.toLocaleString('ko-KR') + '원' : price.toFixed(4) + '원'
}
function formatRate(rate, change) {
  if (rate == null) return '-'
  if (change === 'EVEN' || Math.abs(rate) < 0.000001) return '0.00%'
  const sign = change === 'RISE' ? '+' : '-'
  return sign + (Math.abs(rate) * 100).toFixed(2) + '%'
}
function changeClass(change) {
  if (change === 'RISE') return 'up'
  if (change === 'FALL') return 'down'
  return 'flat'
}
</script>

<style scoped>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

.home-wrapper {
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
  background: var(--color-bg-page, #f8fafc);
}

.grand-hero {
  position: relative;
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  overflow: hidden;
}

/* 403 에러 발생 시 영상 대신 노출될 안전한 그라데이션 백그라운드 */
.video-fallback {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(120deg, #fdfbfb 0%, #ebedee 100%);
  background-size: 200% 200%;
  animation: gradientMove 8s ease infinite;
  z-index: -1;
}

@keyframes gradientMove {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.video-bg {
  position: absolute;
  top: 50%;
  left: 50%;
  min-width: 100%;
  min-height: 100%;
  width: auto;
  height: auto;
  transform: translateX(-50%) translateY(-50%);
  z-index: 0;
  object-fit: cover;
  opacity: 0.6;
}

.video-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(2px);
  z-index: 1;
}

.grand-content {
  position: relative;
  z-index: 10;
  animation: fadeUp 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.grand-eyebrow {
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.4em;
  color: var(--color-primary, #3b82f6);
  margin-bottom: 24px;
}

.grand-title {
  font-size: 4.8rem;
  font-weight: 800;
  line-height: 1.2;
  letter-spacing: -0.04em;
  color: #0f172a;
  margin-bottom: 28px;
}

.text-gradient {
  background: linear-gradient(135deg, #2563eb 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.grand-desc {
  font-size: 1.2rem;
  font-weight: 500;
  color: #475569;
  max-width: 850px;
  margin: 0 auto;
  line-height: 1.6;
  word-break: keep-all;
}

.scroll-indicator {
  position: absolute;
  bottom: 40px;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.3s;
  color: #334155;
}
.scroll-indicator:hover { opacity: 1; }

.mouse {
  width: 26px;
  height: 40px;
  border: 2px solid #334155;
  border-radius: 14px;
  position: relative;
}
.wheel {
  width: 4px;
  height: 8px;
  background: #334155;
  border-radius: 2px;
  position: absolute;
  top: 6px;
  left: 50%;
  transform: translateX(-50%);
  animation: scrollWheel 1.5s infinite;
}
.scroll-text {
  font-size: 12px;
  letter-spacing: 0.2em;
  font-weight: 700;
}

@keyframes scrollWheel {
  0% { top: 6px; opacity: 1; }
  100% { top: 18px; opacity: 0; }
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(40px); }
  to { opacity: 1; transform: translateY(0); }
}

.dashboard-container {
  min-height: 100vh;
  background: var(--color-bg-page, #ffffff);
  position: relative;
  z-index: 20;
  border-top-left-radius: 30px;
  border-top-right-radius: 30px;
  box-shadow: 0 -10px 40px rgba(0,0,0,0.05);
}

.home { min-height: 100vh; padding-top: 40px;}
.section-inner { max-width: 1100px; margin: 0 auto; padding: 0 24px; }
.section-header { display: flex; align-items: center; gap: 12px; margin-bottom: 18px; }
.section-title { font-size: 1.2rem; font-weight: 700; margin: 0; letter-spacing: -0.01em; }
.section-title.center { text-align: center; margin-bottom: 28px; }
.section-link { margin-left: auto; font-size: 0.85rem; color: var(--color-primary); text-decoration: none; font-weight: 600; }
.section-link:hover { text-decoration: underline; }

.hero-section { padding: 20px 24px 56px; }
.hero-grid { display: grid; grid-template-columns: 1fr 1.3fr; gap: 2.5rem; align-items: center; }
.hero-cards { display: flex; gap: 14px; width: 100%; }
.hero-cards-col { display: flex; flex-direction: column; gap: 14px; flex: 1; min-width: 0; }

.eyebrow { font-size: 13px; font-weight: 700; letter-spacing: 0.1em; color: var(--color-primary); margin: 0 0 14px; }
.hero-title { font-size: 2.4rem; font-weight: 700; line-height: 1.35; margin: 0 0 16px; letter-spacing: -0.03em; }
.hero-desc { font-size: 1rem; color: var(--color-text-secondary); line-height: 1.7; margin: 0 0 26px; font-weight: 500; }
.hero-btns { display: flex; gap: 10px; flex-wrap: wrap; }

.btn { display: inline-flex; align-items: center; gap: 6px; padding: 12px 22px; border-radius: var(--radius-md); font-size: 0.9rem; font-weight: 600; text-decoration: none; cursor: pointer; border: none; transition: all 0.15s; }
.btn i { font-size: 18px; }
.btn-primary { background: var(--color-primary); color: white; }
.btn-primary:hover { background: var(--color-primary-hover); transform: translateY(-2px); }
.btn-outline { background: var(--color-bg-card); color: var(--color-text-primary); border: 1px solid var(--color-border-strong); }
.btn-outline:hover { background: var(--color-bg-secondary); transform: translateY(-2px); }

.hero-graph-card { background: var(--color-bg-card); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: 1.2rem 1.4rem; transition: border-color 0.15s, box-shadow 0.15s, transform 0.15s; }
.hero-graph-card:hover { border-color: var(--color-primary); box-shadow: 0 8px 20px rgba(0,0,0,0.06); transform: translateY(-3px); }
.graph-label { font-size: 12px; color: var(--color-text-secondary); margin: 0 0 6px; font-weight: 600; }
.graph-value { font-size: 1.3rem; font-weight: 700; margin: 0 0 12px; letter-spacing: -0.01em; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.graph-rate { font-size: 0.85rem; font-weight: 600; }
.graph-loading { font-size: 0.9rem; color: var(--color-text-tertiary); }
.graph-svg { width: 100%; height: 72px; display: block; }

.forex-card { flex: 1; display: flex; flex-direction: column; }
.forex-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.forex-header .graph-label { margin-bottom: 0; font-size: 12px; }
.forex-list { flex: 1; display: flex; flex-direction: column; justify-content: space-between; gap: 12px; margin-top: 6px; }
.forex-item { display: flex; justify-content: space-between; align-items: center; padding-bottom: 12px; border-bottom: 1px dashed var(--color-border); }
.forex-item:last-child { padding-bottom: 0; border-bottom: none; }
.forex-name-group { display: flex; align-items: center; gap: 8px; }
.forex-flag { font-size: 16px; }
.forex-name { font-size: 0.95rem; font-weight: 600; color: var(--color-text-primary); }
.forex-price-group { display: flex; flex-direction: column; align-items: flex-end; }
.forex-price { font-size: 1rem; font-weight: 700; letter-spacing: -0.01em; }
.forex-rate { font-size: 0.8rem; font-weight: 600; margin-top: 2px; }

.preview-section { padding: 0 0 56px; }
.preview-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.live-dot { padding: 4px 10px; background: #f0fdf4; color: #16a34a; border-radius: 20px; font-size: 0.7rem; font-weight: 700; }
.pulse { animation: pulse-green 2s infinite; }
@keyframes pulse-green { 0% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.4); } 70% { box-shadow: 0 0 0 6px rgba(22, 163, 74, 0); } 100% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0); } }

.metric-card { background: var(--color-bg-secondary); border-radius: var(--radius-md); padding: 1.2rem; text-decoration: none; color: inherit; display: block; transition: all 0.2s; border: 1px solid transparent; }
.metric-card:hover { background: var(--color-primary-light); transform: translateY(-4px); border-color: rgba(59, 130, 246, 0.2); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.ai-card { border: 1px solid var(--color-primary); background: linear-gradient(135deg, #ffffff 0%, #f0f4ff 100%); }
.metric-card.skeleton { height: 90px; background: linear-gradient(90deg, #eee 25%, #f5f5f5 50%, #eee 75%); background-size: 200% 100%; animation: shimmer 1.4s infinite; }
.metric-label { font-size: 0.85rem; font-weight: 600; color: var(--color-text-secondary); margin: 0 0 8px; }
.metric-value { font-size: 1.15rem; font-weight: 700; margin: 0 0 6px; letter-spacing: -0.02em; }
.metric-rate { font-size: 0.85rem; font-weight: 600; margin: 0; }
.metric-unit { font-size: 0.75rem; font-weight: 500; color: var(--color-text-tertiary); margin-left: 4px; }

.up { color: var(--color-up); }
.down { color: var(--color-down); }
.flat { color: var(--color-text-tertiary); }

.feature-section { padding: 0 0 72px; }
.feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
.feature-card { background: var(--color-bg-card); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: 2.5rem 1.5rem; text-align: center; text-decoration: none; color: inherit; display: block; transition: all 0.2s; }
.feature-card:hover { transform: translateY(-6px); border-color: var(--color-primary-light); box-shadow: 0 10px 25px rgba(0,0,0,0.05); }
.feature-card--active { border: 2px solid var(--color-primary); }
.feature-card--active:hover { border-color: var(--color-primary-hover); }

.feature-icon { font-size: 32px; color: var(--color-text-tertiary); margin-bottom: 16px; display: block; }
.feature-icon--active { font-size: 32px; color: var(--color-primary); margin-bottom: 16px; display: block; }
.feature-name { font-size: 1.1rem; font-weight: 700; margin: 0 0 8px; }
.feature-status { font-size: 0.85rem; font-weight: 500; color: var(--color-text-secondary); margin: 0 0 20px; }
.feature-status--live { color: var(--color-primary); font-weight: 600; }

.feature-btn { display: inline-block; font-size: 0.85rem; padding: 8px 18px; border-radius: var(--radius-md); border: 1px solid var(--color-border-strong); color: var(--color-text-primary); font-weight: 600; text-decoration: none; transition: background 0.15s; }
.feature-btn:hover { background: var(--color-bg-secondary); }
.feature-btn--primary { background: var(--color-primary); color: white; border: none; }
.feature-btn--primary:hover { background: var(--color-primary-hover); }

@media (max-width: 1024px) { .hero-grid { grid-template-columns: 1fr; } .hero-cards { flex-direction: row; } .grand-title { font-size: 3.8rem; } }
@media (max-width: 600px) { .hero-cards { flex-direction: column; } .preview-grid { grid-template-columns: repeat(2, 1fr); } .feature-grid { grid-template-columns: 1fr; } .grand-title { font-size: 2.8rem; } }
</style>