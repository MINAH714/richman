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

      <!-- 우측 사이드 -->
      <aside class="info-section">

        <!-- 현재가 정보 -->
        <div class="info-card">
          <h3>현재가 정보</h3>
          <div v-if="isLoading" class="info-loading">불러오는 중...</div>
          <div v-else-if="ticker" class="price-info">
            <div class="info-row">
              <span class="info-label">현재가</span>
              <span class="info-value price">{{ formatPrice(ticker.trade_price) }}</span>
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
              <span class="info-value">{{ ticker.acc_trade_volume_24h?.toFixed(3) }}</span>
            </div>
          </div>
          <div v-else class="info-loading">데이터를 불러오는 중...</div>
        </div>

        <!-- 코인 기본 정보 -->
        <div class="info-card">
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

        <!-- ── 감성 분석 카드 ─────────────────────────────── -->
        <div class="info-card sentiment-card">
          <div class="sentiment-card-header">
            <h3>뉴스 감성 분석</h3>
            <span v-if="sentiment.analyzed_at" class="sentiment-timestamp">
              {{ formattedSentimentAt }}
            </span>
          </div>

          <!-- 로딩 스켈레톤 -->
          <div v-if="sentimentLoading" class="sentiment-skeleton">
            <div class="skel-bar" v-for="n in 3" :key="n" />
          </div>

          <!-- 결과 있음 -->
          <div v-else-if="hasResult" class="sentiment-result">
            <p class="sentiment-summary">{{ sentiment.summary }}</p>

            <div class="sentiment-dominant" :class="dominantClass">
              <span>{{ dominantEmoji }}</span>
              <span>{{ dominantLabel }}</span>
              <span class="dominant-pct">{{ dominantPct }}%</span>
            </div>

            <div class="sentiment-gauges">
              <div class="sg-row" v-for="row in gaugeRows" :key="row.key">
                <span class="sg-icon">{{ row.icon }}</span>
                <span class="sg-label" :style="{ color: row.color }">{{ row.label }}</span>
                <div class="sg-track">
                  <div
                    class="sg-fill"
                    :style="{ width: animatedScores[row.key] + '%', background: row.gradient }"
                  >
                    <span v-if="animatedScores[row.key] > 10" class="sg-inner-pct">
                      {{ Math.round(animatedScores[row.key]) }}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 빈 상태 -->
          <div v-else class="sentiment-empty">
            <span>📡 분석 데이터 없음</span>
          </div>

          <!-- 액션 버튼 행 -->
          <div class="sentiment-actions">
            <button
              class="sentiment-run-btn"
              :disabled="sentimentAnalyzing"
              @click="runSentiment"
            >
              <span v-if="sentimentAnalyzing" class="btn-analyzing">
                <span class="btn-dots"><i/><i/><i/></span> 분석 중
              </span>
              <span v-else>🔍 다시 분석</span>
            </button>
            <router-link
              class="sentiment-full-link"
              :to="{ name: 'crypto-sentiment', params: { market: marketId }, query: { name: coinMeta?.korean_name } }"
            >
              전체 보기 →
            </router-link>
          </div>
        </div>

      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
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

const marketId   = ref(route.params.market)
const coinSymbol = computed(() => marketId.value.split('-')[1])
const coinMeta   = computed(() => cryptoStore.coins.find(c => c.market === marketId.value) ?? null)

const isLoading = ref(true)
const ticker    = ref(null)
const candles   = ref([])

// ── ApexCharts ────────────────────────────────────────────
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
    labels: { style: { fontFamily: 'IBM Plex Mono, monospace', fontSize: '11px' } },
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
      colors: { upward: '#ef4444', downward: '#3b82f6' },
    },
  },
  tooltip: { x: { format: 'yyyy-MM-dd' } },
  grid: { borderColor: '#e2ecf9' },
}))

const chartSeries = computed(() => [{
  name: marketId.value,
  data: candles.value.map(c => ({
    x: new Date(c.candle_date_time_kst),
    y: [c.opening_price, c.high_price, c.low_price, c.trade_price],
  })),
}])

// ── 코인 상세 API ─────────────────────────────────────────
async function fetchCoinDetail() {
  isLoading.value = true
  try {
    const { data } = await cryptoAPI.getCoinDetail(marketId.value)
    ticker.value  = data.ticker
    candles.value = data.candles
  } catch (e) {
    console.error('상세 정보 로드 실패:', e)
  } finally {
    isLoading.value = false
  }
}

// ── 10초 폴링 ─────────────────────────────────────────────
let pollingTimer = null

async function pollTicker() {
  try {
    const { data } = await cryptoAPI.getCoinDetail(marketId.value)
    ticker.value = data.ticker
  } catch (e) {
    console.error('ticker 폴링 실패:', e)
  }
}

// ── 감성 분석 ─────────────────────────────────────────────
const sentiment = ref({
  positive_score: 0,
  neutral_score:  0,
  negative_score: 0,
  summary:        '',
  analyzed_at:    '',
})
const sentimentLoading   = ref(false)
const sentimentAnalyzing = ref(false)
const animatedScores     = ref({ positive: 0, neutral: 0, negative: 0 })

// 결과 유무 판단
const hasResult = computed(() =>
  sentiment.value.positive_score + sentiment.value.neutral_score + sentiment.value.negative_score > 0
)

function animateGauges() {
  const targets = {
    positive: Math.round(sentiment.value.positive_score * 100),
    neutral:  Math.round(sentiment.value.neutral_score  * 100),
    negative: Math.round(sentiment.value.negative_score * 100),
  }
  animatedScores.value = { positive: 0, neutral: 0, negative: 0 }

  const DURATION = 700
  const STEP     = 16
  let elapsed    = 0

  const timer = setInterval(() => {
    elapsed += STEP
    const progress = Math.min(elapsed / DURATION, 1)
    const ease = 1 - Math.pow(1 - progress, 3)
    animatedScores.value = {
      positive: targets.positive * ease,
      neutral:  targets.neutral  * ease,
      negative: targets.negative * ease,
    }
    if (progress >= 1) clearInterval(timer)
  }, STEP)
}

async function loadSentimentCache() {
  sentimentLoading.value = true
  try {
    const { data } = await cryptoAPI.getSentimentCached(marketId.value)
    sentiment.value = { ...sentiment.value, ...data }
    await nextTick()
    animateGauges()
  } catch {
    // 캐시 없음 — 조용히 무시
  } finally {
    sentimentLoading.value = false
  }
}

async function runSentiment() {
  sentimentAnalyzing.value = true
  try {
    const { data } = await cryptoAPI.analyzeSentiment(
      marketId.value,
      coinMeta.value?.korean_name ?? ''
    )
    sentiment.value = { ...data }
    await nextTick()
    animateGauges()
  } catch (e) {
    console.error('감성 분석 실패:', e)
  } finally {
    sentimentAnalyzing.value = false
  }
}

// 게이지 행 정의
const gaugeRows = [
  { key: 'positive', label: '긍정', icon: '😊', color: '#4ade80', gradient: 'linear-gradient(90deg,#166534,#4ade80)' },
  { key: 'neutral',  label: '중립', icon: '😐', color: '#94a3b8', gradient: 'linear-gradient(90deg,#334155,#94a3b8)' },
  { key: 'negative', label: '부정', icon: '😰', color: '#f87171', gradient: 'linear-gradient(90deg,#7f1d1d,#f87171)' },
]

// 도미넌트
const dominant = computed(() => {
  const s = sentiment.value
  if (s.positive_score >= s.neutral_score && s.positive_score >= s.negative_score) return 'positive'
  if (s.negative_score >= s.neutral_score) return 'negative'
  return 'neutral'
})
const dominantClass = computed(() =>
  ({ positive: 'chip-pos', neutral: 'chip-neu', negative: 'chip-neg' }[dominant.value])
)
const dominantEmoji = computed(() =>
  ({ positive: '😊', neutral: '😐', negative: '😰' }[dominant.value])
)
const dominantLabel = computed(() =>
  ({ positive: '긍정 우세', neutral: '중립', negative: '부정 우세' }[dominant.value])
)
const dominantPct = computed(() =>
  Math.round((sentiment.value[`${dominant.value}_score`] ?? 0) * 100)
)
const formattedSentimentAt = computed(() => {
  if (!sentiment.value.analyzed_at) return ''
  try {
    return new Date(sentiment.value.analyzed_at).toLocaleString('ko-KR', {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
    })
  } catch { return '' }
})

// ── 라이프사이클 ──────────────────────────────────────────
function goBack() { router.push('/crypto') }

onMounted(async () => {
  if (cryptoStore.coins.length === 0) await cryptoStore.loadCoins()
  if (authStore.isLoggedIn && cryptoStore.watchlist.length === 0) {
    await cryptoStore.loadWatchlist()
  }
  await fetchCoinDetail()
  loadSentimentCache()
  pollingTimer = setInterval(pollTicker, 10_000)
})

onUnmounted(() => { clearInterval(pollingTimer) })

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
  if (vol >= 100_000_000)       return (vol / 100_000_000).toFixed(1) + '억'
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

/* ── 헤더 ── */
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
.coin-title { display: flex; align-items: center; gap: 10px; flex: 1; }
.market-id  { font-size: 1.5rem; font-weight: 700; margin: 0; }
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
  50%       { opacity: 0.5; }
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
.fav-btn.active { background: #fef3c7; border-color: #f59e0b; color: #d97706; }
.fav-btn:hover  { opacity: 0.8; }

/* ── 그리드 ── */
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

/* ── 공통 카드 ── */
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
  margin: 0 0 16px;
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
.up   { color: #ef4444; }
.down { color: #3b82f6; }
.flat { color: #6b7280; }

/* ── 감성 분석 카드 ── */
.sentiment-card { padding: 18px 20px; }

.sentiment-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.sentiment-card-header h3 { margin: 0; }
.sentiment-timestamp {
  font-size: 10px;
  color: #94a3b8;
  font-weight: 400;
  letter-spacing: 0;
  text-transform: none;
}

/* 결과 래퍼 */
.sentiment-result { display: flex; flex-direction: column; }

/* 요약 */
.sentiment-summary {
  font-size: 12px;
  color: #64748b;
  margin: 0 0 12px;
  line-height: 1.5;
  font-style: italic;
}

/* 도미넌트 칩 */
.sentiment-dominant {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  border-radius: 20px;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 700;
  margin-bottom: 14px;
  width: fit-content;
}
.chip-pos { background: rgba(74,222,128,0.12); border: 1px solid rgba(74,222,128,0.25); color: #16a34a; }
.chip-neu { background: rgba(148,163,184,0.12); border: 1px solid rgba(148,163,184,0.25); color: #64748b; }
.chip-neg { background: rgba(248,113,113,0.12); border: 1px solid rgba(248,113,113,0.25); color: #dc2626; }
.dominant-pct { opacity: 0.75; }

/* 게이지 */
.sentiment-gauges { display: flex; flex-direction: column; gap: 8px; }
.sg-row  { display: flex; align-items: center; gap: 7px; }
.sg-icon { font-size: 13px; flex-shrink: 0; }
.sg-label {
  font-size: 11px;
  font-weight: 600;
  width: 28px;
  flex-shrink: 0;
}
.sg-track {
  flex: 1;
  height: 22px;
  background: #f1f5f9;
  border-radius: 5px;
  overflow: hidden;
}
.sg-fill {
  height: 100%;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 6px;
  min-width: 0;
  transition: width 16ms linear;
}
.sg-inner-pct {
  font-size: 10px;
  font-weight: 700;
  color: rgba(255,255,255,0.95);
  white-space: nowrap;
}

/* 빈 상태 */
.sentiment-empty {
  text-align: center;
  padding: 12px 0;
  font-size: 12px;
  color: #94a3b8;
}

/* 스켈레톤 */
.sentiment-skeleton { display: flex; flex-direction: column; gap: 8px; padding: 4px 0; }
.skel-bar {
  height: 22px;
  border-radius: 5px;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2ecf9 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
}
.skel-bar:nth-child(1) { width: 100%; }
.skel-bar:nth-child(2) { width: 70%; }
.skel-bar:nth-child(3) { width: 50%; }
@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* 액션 */
.sentiment-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid #f1f5f9;
}
.sentiment-run-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 7px 13px;
  border-radius: 6px;
  border: 1px solid #d0e2f5;
  background: #f8faff;
  color: #3b6fd4;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  font-family: 'IBM Plex Mono', monospace;
  transition: background 0.15s;
}
.sentiment-run-btn:hover:not(:disabled) { background: #e8f0fe; }
.sentiment-run-btn:disabled { opacity: 0.45; cursor: not-allowed; }
.sentiment-full-link {
  font-size: 11px;
  font-weight: 600;
  color: #6b7280;
  text-decoration: none;
  transition: color 0.15s;
}
.sentiment-full-link:hover { color: #3b6fd4; }

/* 점 애니메이션 */
.btn-analyzing { display: inline-flex; align-items: center; gap: 5px; }
.btn-dots { display: inline-flex; gap: 2px; align-items: center; }
.btn-dots i {
  display: block;
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: currentColor;
  font-style: normal;
  animation: bdot 1s ease-in-out infinite;
}
.btn-dots i:nth-child(2) { animation-delay: 0.15s; }
.btn-dots i:nth-child(3) { animation-delay: 0.30s; }
@keyframes bdot {
  0%, 60%, 100% { transform: translateY(0); }
  30%           { transform: translateY(-3px); }
}
</style>