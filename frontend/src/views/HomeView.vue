<template>
  <div class="home">

    <section class="hero-section">
      <div class="section-inner hero-grid">

        <div class="hero-text">
          <p class="eyebrow">SMART FINANCIAL PLATFORM</p>
          <h1 class="hero-title">흩어진 자산을<br>하나의 시야로</h1>
          <p class="hero-desc">
            소비 · 주식 · 크립토 데이터를 통합 분석하고<br>
            AI가 맞춤 인사이트를 제공합니다
          </p>
          <div class="hero-btns">
            <router-link to="/chat" class="btn btn-primary">
              <i class="ti ti-robot" aria-hidden="true"></i> AI 비서 시작
            </router-link>
            <router-link to="/consumption" class="btn btn-outline">
              <i class="ti ti-building-bank" aria-hidden="true"></i> 예적금
            </router-link>
            <router-link to="/stocks/watchlist" class="btn btn-outline">
              <i class="ti ti-chart-candle" aria-hidden="true"></i> 주식/현물
            </router-link>
          </div>
        </div>

        <div class="hero-graph-card">
          <p class="graph-label">실시간 시세 추이 (BTC)</p>
          <p class="graph-value">
            {{ formatPrice(btcTicker?.trade_price) }}
            <span class="graph-rate" :class="changeClass(btcTicker?.change)">
              {{ formatRate(btcTicker?.change_rate) }}
            </span>
          </p>
          <svg viewBox="0 0 280 90" class="graph-svg" role="img" aria-label="비트코인 30일 가격 추이">
            <polyline :points="chartPoints" fill="none" stroke="#378ADD" stroke-width="2.5" />
            <polygon :points="chartAreaPoints" fill="#E6F1FB" opacity="0.6" />
          </svg>
        </div>

      </div>
    </section>

    <section class="preview-section">
      <div class="section-inner">
        <div class="section-header">
          <h2 class="section-title">실시간 시세</h2>
          <span class="live-dot">LIVE</span>
          <router-link to="/crypto" class="section-link">전체 보기 →</router-link>
        </div>

        <div v-if="isLoading" class="preview-grid">
          <div class="metric-card skeleton" v-for="n in 4" :key="n" />
        </div>

        <div v-else class="preview-grid">
          <router-link
            v-for="coin in topCoins"
            :key="coin.market"
            :to="`/crypto/${coin.market}`"
            class="metric-card"
          >
            <p class="metric-label">{{ coin.coin_symbol }}</p>
            <p class="metric-value">{{ formatPrice(coin.trade_price) }}</p>
            <p class="metric-rate" :class="changeClass(coin.change)">
              {{ formatRate(coin.change_rate) }}
            </p>
          </router-link>

          <router-link to="/chat" class="metric-card">
            <p class="metric-label">AI 금융 비서</p>
            <p class="metric-value">포트폴리오 분석</p>
            <p class="metric-rate up">지금 상담하기 →</p>
          </router-link>
        </div>
      </div>
    </section>

    <section class="feature-section">
      <div class="section-inner">
        <h2 class="section-title center">기능 바로가기</h2>

        <div class="feature-grid">
          <router-link to="/consumption" class="feature-card">
            <i class="ti ti-building-bank feature-icon" aria-hidden="true"></i>
            <p class="feature-name">예적금 랭킹</p>
            <p class="feature-status">최고 금리 찾기</p>
            <span class="feature-btn">둘러보기</span>
          </router-link>

          <router-link to="/stocks/chart" class="feature-card">
            <i class="ti ti-chart-line feature-icon" aria-hidden="true"></i>
            <p class="feature-name">주식 및 현물</p>
            <p class="feature-status">실시간 시세 차트</p>
            <span class="feature-btn">둘러보기</span>
          </router-link>

          <router-link to="/stocks/watchlist" class="feature-card">
            <i class="ti ti-brand-youtube feature-icon" aria-hidden="true"></i>
            <p class="feature-name">관심 종목</p>
            <p class="feature-status">유튜브 트렌드 분석</p>
            <span class="feature-btn">둘러보기</span>
          </router-link>

          <router-link to="/crypto/buzz" class="feature-card feature-card--active">
            <i class="ti ti-flame feature-icon feature-icon--active" aria-hidden="true"></i>
            <p class="feature-name">크립토 버즈</p>
            <p class="feature-status feature-status--live">실시간 감성분석</p>
            <span class="feature-btn feature-btn--primary">바로가기 →</span>
          </router-link>

          <router-link to="/chat" class="feature-card">
            <i class="ti ti-message-chatbot feature-icon" aria-hidden="true"></i>
            <p class="feature-name">AI 맞춤 추천</p>
            <p class="feature-status">나만의 금융 비서</p>
            <span class="feature-btn">둘러보기</span>
          </router-link>

          <router-link to="/insight" class="feature-card">
            <i class="ti ti-map-pin feature-icon" aria-hidden="true"></i>
            <p class="feature-name">주변 은행 검색</p>
            <p class="feature-status">내 위치 기반 경로안내</p>
            <span class="feature-btn">둘러보기</span>
          </router-link>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { cryptoAPI } from '@/api/crypto'

const allCoins  = ref([])
const isLoading = ref(true)
const candles   = ref([])

const topCoins = computed(() =>
  [...allCoins.value]
    .sort((a, b) => (b.acc_trade_price_24h ?? 0) - (a.acc_trade_price_24h ?? 0))
    .slice(0, 3)
)

const btcTicker = computed(() =>
  allCoins.value.find(c => c.market === 'KRW-BTC')
)

// ── 캔들 데이터 → SVG 라인 좌표 변환 ──────────────────────
const chartPoints = computed(() => {
  if (!candles.value.length) return '0,70 280,70'
  const prices = candles.value.map(c => c.trade_price).reverse()
  const min = Math.min(...prices)
  const max = Math.max(...prices)
  const range = max - min || 1
  const stepX = 280 / (prices.length - 1)

  return prices
    .map((p, i) => {
      const x = (i * stepX).toFixed(1)
      const y = (90 - ((p - min) / range) * 80 - 5).toFixed(1)
      return `${x},${y}`
    })
    .join(' ')
})

const chartAreaPoints = computed(() => `0,90 ${chartPoints.value} 280,90`)

async function loadCoins() {
  try {
    const { data } = await cryptoAPI.getCoins()
    allCoins.value = data
  } catch (e) {
    console.error('코인 로드 실패:', e)
  } finally {
    isLoading.value = false
  }
}

async function loadBtcCandles() {
  try {
    const { data } = await cryptoAPI.getCoinDetail('KRW-BTC')
    candles.value = data.candles ?? []
  } catch (e) {
    console.error('캔들 로드 실패:', e)
  }
}

let timer = null
onMounted(() => {
  loadCoins()
  loadBtcCandles()
  timer = setInterval(loadCoins, 10_000)
})
onUnmounted(() => clearInterval(timer))

function formatPrice(price) {
  if (price == null) return '-'
  return price >= 100
    ? price.toLocaleString('ko-KR') + '원'
    : price.toFixed(4) + '원'
}
function formatRate(rate) {
  if (rate == null) return '-'
  return (rate >= 0 ? '+' : '') + (rate * 100).toFixed(2) + '%'
}
function changeClass(change) {
  if (change === 'RISE') return 'up'
  if (change === 'FALL') return 'down'
  return 'flat'
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: var(--color-bg-page);
  font-family: var(--font-main);
  color: var(--color-text-primary);
}

.section-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px;
}
.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
}
.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.01em;
}
.section-title.center { text-align: center; margin-bottom: 28px; }
.section-link {
  margin-left: auto;
  font-size: 0.8rem;
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 500;
}
.section-link:hover { text-decoration: underline; }

/* ── HERO ── */
.hero-section { padding: 48px 24px 56px; }
.hero-grid {
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  gap: 2.5rem;
  align-items: center;
}
.eyebrow {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.1em;
  color: var(--color-primary);
  margin: 0 0 14px;
}
.hero-title {
  font-size: 2.3rem;
  font-weight: 600;
  line-height: 1.35;
  margin: 0 0 16px;
  letter-spacing: -0.02em;
}
.hero-desc {
  font-size: 0.95rem;
  color: var(--color-text-secondary);
  line-height: 1.7;
  margin: 0 0 26px;
  font-weight: 400;
}
.hero-btns { display: flex; gap: 10px; flex-wrap: wrap; }

.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 11px 20px;
  border-radius: var(--radius-md);
  font-size: 0.86rem;
  font-weight: 500;
  font-family: var(--font-main);
  text-decoration: none;
  cursor: pointer;
  border: none;
  transition: all 0.15s;
}
.btn i { font-size: 16px; }
.btn-primary { background: var(--color-primary); color: white; }
.btn-primary:hover { background: var(--color-primary-hover); }
.btn-outline {
  background: var(--color-bg-card);
  color: var(--color-text-primary);
  border: 0.5px solid var(--color-border-strong);
}
.btn-outline:hover { background: var(--color-bg-secondary); }

/* 히어로 그래프 카드 */
.hero-graph-card {
  background: var(--color-bg-card);
  border: 0.5px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1.4rem;
}
.graph-label { font-size: 12px; color: var(--color-text-secondary); margin: 0 0 6px; }
.graph-value {
  font-size: 1.4rem;
  font-weight: 500;
  margin: 0 0 14px;
  letter-spacing: -0.01em;
}
.graph-rate { font-size: 0.82rem; font-weight: 500; margin-left: 6px; }
.graph-svg { width: 100%; height: 90px; display: block; }

/* ── 실시간 시세 ── */
.preview-section { padding: 0 0 56px; }
.preview-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.live-dot {
  padding: 3px 9px;
  background: #f0fdf4;
  color: #16a34a;
  border-radius: 20px;
  font-size: 0.68rem;
  font-weight: 600;
}

.metric-card {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  padding: 1rem 1.1rem;
  text-decoration: none;
  color: inherit;
  display: block;
  transition: background 0.15s;
}
.metric-card:hover { background: var(--color-primary-light); }
.metric-card.skeleton {
  height: 84px;
  background: linear-gradient(90deg, #eee 25%, #e0e0e0 50%, #eee 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
}
@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
.metric-label { font-size: 0.78rem; color: var(--color-text-secondary); margin: 0 0 6px; }
.metric-value { font-size: 1.05rem; font-weight: 500; margin: 0 0 4px; letter-spacing: -0.01em; }
.metric-rate { font-size: 0.78rem; font-weight: 500; margin: 0; }

.up   { color: var(--color-up); }
.down { color: var(--color-down); }
.flat { color: var(--color-text-tertiary); }

/* ── 기능 카드 확장 (F1301) ── */
.feature-section { padding: 0 0 72px; }
.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); /* 명세서 반영을 위해 유동적 3열/2열 적용 */
  gap: 16px;
}
.feature-card {
  background: var(--color-bg-card);
  border: 0.5px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 2rem 1.5rem;
  text-align: center;
  text-decoration: none;
  color: inherit;
  display: block;
  transition: border-color 0.15s, transform 0.15s;
}
.feature-card:hover { transform: translateY(-4px); border-color: var(--color-primary-light); }
.feature-card--active {
  border: 2px solid var(--color-primary);
}
.feature-card--active:hover { border-color: var(--color-primary-hover); }

.feature-icon {
  font-size: 28px;
  color: var(--color-text-tertiary);
  margin-bottom: 14px;
  display: block;
}
.feature-icon--active { color: var(--color-primary); }

.feature-name { font-size: 1rem; font-weight: 600; margin: 0 0 6px; }
.feature-status { font-size: 0.78rem; color: var(--color-text-secondary); margin: 0 0 16px; }
.feature-status--live { color: var(--color-primary); font-weight: 500; }

.feature-btn {
  display: inline-block;
  font-size: 0.8rem;
  padding: 7px 16px;
  border-radius: var(--radius-md);
  border: 0.5px solid var(--color-border-strong);
  color: var(--color-text-primary);
  text-decoration: none;
  transition: background 0.15s;
}
.feature-btn:hover { background: var(--color-bg-secondary); }
.feature-btn--primary {
  background: var(--color-primary);
  color: white;
  border: none;
  font-weight: 500;
}
.feature-btn--primary:hover { background: var(--color-primary-hover); }

/* 반응형 처리 */
@media (max-width: 900px) {
  .hero-grid { grid-template-columns: 1fr; }
  .preview-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 600px) {
  .preview-grid { grid-template-columns: 1fr; }
  .feature-grid { grid-template-columns: 1fr; }
}
</style>