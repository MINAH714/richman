<template>
  <div class="home">

    <!-- ── HERO ──────────────────────────────────────────── -->
    <section class="hero">
      <div class="hero-inner">
        <p class="hero-eyebrow">SMART FINANCIAL PLATFORM</p>
        <h1 class="hero-title">소비 · 주식 · 크립토<br>한 곳에서</h1>
        <p class="hero-desc">
          AI가 내 금융 데이터를 분석하고<br>
          실질적인 인사이트를 제공합니다
        </p>
        <div class="hero-actions">
          <router-link to="/crypto" class="btn btn-primary">
            🪙 크립토 보러가기
          </router-link>
          <router-link to="/login" class="btn btn-outline" v-if="!authStore.isLoggedIn">
            로그인
          </router-link>
        </div>
      </div>
    </section>

    <!-- ── 실시간 코인 미리보기 ───────────────────────────── -->
    <section class="preview-section">
      <div class="section-inner">
        <div class="section-header">
          <h2 class="section-title">실시간 시세</h2>
          <span class="live-dot">LIVE</span>
          <router-link to="/crypto" class="section-link">전체 보기 →</router-link>
        </div>

        <div v-if="isLoading" class="preview-grid">
          <div class="coin-card skeleton" v-for="n in 5" :key="n" />
        </div>

        <div v-else class="preview-grid">
          <router-link
            v-for="coin in topCoins"
            :key="coin.market"
            :to="`/crypto/${coin.market}`"
            class="coin-card"
          >
            <div class="coin-card-top">
              <span class="coin-symbol">{{ coin.coin_symbol }}</span>
              <span class="coin-change" :class="changeClass(coin.change)">
                {{ formatRate(coin.change_rate) }}
              </span>
            </div>
            <p class="coin-name">{{ coin.korean_name }}</p>
            <p class="coin-price">{{ formatPrice(coin.trade_price) }}</p>
            <p class="coin-volume">거래대금 {{ formatVolume(coin.acc_trade_price_24h) }}</p>
          </router-link>
        </div>
      </div>
    </section>

    <!-- ── 기능 카드 3개 ──────────────────────────────────── -->
    <section class="feature-section">
      <div class="section-inner">
        <h2 class="section-title center">주요 기능</h2>

        <div class="feature-grid">

          <!-- 크립토 — 완성 -->
          <router-link to="/crypto" class="feature-card feature-card--active">
            <div class="feature-icon">🪙</div>
            <h3 class="feature-name">크립토</h3>
            <p class="feature-desc">
              실시간 시세 · Buzz 지표<br>
              뉴스 감성 분석
            </p>
            <div class="feature-status feature-status--live">사용 가능</div>
            <ul class="feature-list">
              <li>✅ 전체 코인 실시간 시세</li>
              <li>✅ 즐겨찾기</li>
              <li>✅ Social Buzz 점수</li>
              <li>✅ GPT 뉴스 감성 분석</li>
            </ul>
          </router-link>

          <!-- 주식 — 준비중 -->
          <div class="feature-card feature-card--soon">
            <div class="feature-icon">📈</div>
            <h3 class="feature-name">주식</h3>
            <p class="feature-desc">
              기술 지표 시각화<br>
              AI 예측 · 포트폴리오
            </p>
            <div class="feature-status feature-status--soon">준비 중</div>
            <ul class="feature-list">
              <li>⬜ 종목 검색 & 자동완성</li>
              <li>⬜ MA · 볼린저밴드 차트</li>
              <li>⬜ 관심 종목 포트폴리오</li>
              <li>⬜ AI 예측 히스토리</li>
            </ul>
          </div>

          <!-- 소비 — 준비중 -->
          <div class="feature-card feature-card--soon">
            <div class="feature-icon">💳</div>
            <h3 class="feature-name">소비 분석</h3>
            <p class="feature-desc">
              소비 캘린더 · 정산<br>
              AI 소비 리포트
            </p>
            <div class="feature-status feature-status--soon">준비 중</div>
            <ul class="feature-list">
              <li>⬜ 월별 소비 캘린더</li>
              <li>⬜ 카테고리별 분석</li>
              <li>⬜ 스마트 정산 시스템</li>
              <li>⬜ AI 소비 리포트</li>
            </ul>
          </div>

        </div>
      </div>
    </section>

    <!-- ── AI 챗봇 소개 ────────────────────────────────────── -->
    <section class="chatbot-section">
      <div class="section-inner chatbot-inner">
        <div class="chatbot-text">
          <p class="hero-eyebrow">AI INTEGRATION</p>
          <h2 class="section-title">AI 통합 챗봇</h2>
          <p class="chatbot-desc">
            소비 · 주식 · 크립토 실제 데이터를 기반으로<br>
            개인화된 금융 인사이트를 제공합니다
          </p>
          <div class="chatbot-examples">
            <div class="chat-bubble">
              💬 "비트코인 왜 올랐어?"
            </div>
            <div class="chat-bubble chat-bubble--reply">
              🤖 오늘 ETF 승인 기대감으로 3.2% 상승, Buzz Score 72점으로 높은 편입니다.
            </div>
            <div class="chat-bubble">
              💬 "나 이번 달 재정 상태 어때?"
            </div>
            <div class="chat-bubble chat-bubble--reply">
              🤖 총 소비 124만원, 주식 +3.2%, BTC -1.4%. 여유 자금 약 38만원입니다.
            </div>
          </div>
        </div>
        <div class="chatbot-status">
          <div class="status-card">
            <span class="status-icon">🤖</span>
            <p class="status-label">AI 챗봇</p>
            <p class="status-text">전 파트 통합 후<br>출시 예정</p>
            <div class="feature-status feature-status--soon" style="margin-top: 12px;">준비 중</div>
          </div>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { cryptoAPI } from '@/api/crypto'

const authStore = useAuthStore()

const allCoins  = ref([])
const isLoading = ref(true)

// 거래대금 TOP 5
const topCoins = computed(() =>
  [...allCoins.value]
    .sort((a, b) => (b.acc_trade_price_24h ?? 0) - (a.acc_trade_price_24h ?? 0))
    .slice(0, 5)
)

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

// 10초 폴링
let timer = null
onMounted(() => {
  loadCoins()
  timer = setInterval(loadCoins, 10_000)
})
onUnmounted(() => clearInterval(timer))

// ── 포맷 헬퍼 ────────────────────────────────────────────
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
.home {
  min-height: 100vh;
  background: #f0f6ff;
  font-family: 'IBM Plex Mono', monospace;
  color: #0f172a;
}

/* ── 공통 레이아웃 ── */
.section-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px;
}
.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}
.section-title {
  font-size: 1.15rem;
  font-weight: 700;
  margin: 0;
  color: #0f172a;
}
.section-title.center { text-align: center; margin-bottom: 28px; }
.section-link {
  margin-left: auto;
  font-size: 0.8rem;
  color: #3b6fd4;
  text-decoration: none;
  font-weight: 600;
}
.section-link:hover { text-decoration: underline; }

/* ── HERO ── */
.hero {
  padding: 72px 24px 56px;
  text-align: center;
}
.hero-inner { max-width: 600px; margin: 0 auto; }
.hero-eyebrow {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.15em;
  color: #3b6fd4;
  margin: 0 0 16px;
}
.hero-title {
  font-size: 2.2rem;
  font-weight: 800;
  line-height: 1.25;
  margin: 0 0 16px;
  color: #0f172a;
}
.hero-desc {
  font-size: 0.95rem;
  color: #64748b;
  line-height: 1.7;
  margin: 0 0 28px;
}
.hero-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}
.btn {
  padding: 11px 24px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 700;
  font-family: 'IBM Plex Mono', monospace;
  text-decoration: none;
  cursor: pointer;
  border: none;
  transition: all 0.15s;
}
.btn-primary { background: #3b6fd4; color: white; }
.btn-primary:hover { background: #2d5ab8; }
.btn-outline { background: white; color: #3b6fd4; border: 1px solid #3b6fd4; }
.btn-outline:hover { background: #f0f6ff; }

/* ── LIVE 배지 ── */
.live-dot {
  padding: 2px 8px;
  background: #dcfce7;
  color: #16a34a;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 700;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.5; }
}

/* ── 실시간 미리보기 ── */
.preview-section {
  padding: 0 0 48px;
}
.preview-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}
.coin-card {
  background: white;
  border: 1px solid #e2ecf9;
  border-radius: 10px;
  padding: 16px;
  text-decoration: none;
  color: inherit;
  transition: box-shadow 0.15s, border-color 0.15s;
  display: block;
}
.coin-card:hover {
  box-shadow: 0 4px 16px rgba(59,111,212,0.1);
  border-color: #bdd0f5;
}
.coin-card.skeleton {
  height: 110px;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2ecf9 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
}
@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
.coin-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}
.coin-symbol { font-size: 0.9rem; font-weight: 700; }
.coin-change { font-size: 0.8rem; font-weight: 700; }
.coin-name   { font-size: 0.75rem; color: #94a3b8; margin: 0 0 8px; }
.coin-price  { font-size: 0.95rem; font-weight: 700; margin: 0 0 4px; }
.coin-volume { font-size: 0.7rem; color: #94a3b8; margin: 0; }

.up   { color: #ef4444; }
.down { color: #3b82f6; }
.flat { color: #6b7280; }

/* ── 기능 카드 ── */
.feature-section { padding: 48px 0; }
.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}
.feature-card {
  background: white;
  border: 1px solid #e2ecf9;
  border-radius: 12px;
  padding: 28px 24px;
  text-decoration: none;
  color: inherit;
  transition: box-shadow 0.15s;
  display: block;
}
.feature-card--active {
  border-color: #bdd0f5;
  box-shadow: 0 2px 12px rgba(59,111,212,0.08);
}
.feature-card--active:hover {
  box-shadow: 0 6px 24px rgba(59,111,212,0.15);
}
.feature-card--soon {
  opacity: 0.65;
  cursor: default;
}
.feature-icon { font-size: 2rem; margin-bottom: 12px; }
.feature-name {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0 0 8px;
}
.feature-desc {
  font-size: 0.8rem;
  color: #64748b;
  line-height: 1.6;
  margin: 0 0 14px;
}
.feature-status {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 700;
  margin-bottom: 16px;
}
.feature-status--live {
  background: #dcfce7;
  color: #16a34a;
}
.feature-status--soon {
  background: #f1f5f9;
  color: #94a3b8;
}
.feature-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.feature-list li {
  font-size: 0.78rem;
  color: #64748b;
}

/* ── 챗봇 섹션 ── */
.chatbot-section {
  padding: 48px 0 72px;
  background: white;
  border-top: 1px solid #e2ecf9;
}
.chatbot-inner {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 48px;
  align-items: start;
}
.chatbot-desc {
  font-size: 0.9rem;
  color: #64748b;
  line-height: 1.7;
  margin: 8px 0 20px;
}
.chatbot-examples {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.chat-bubble {
  display: inline-block;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 0.8rem;
  line-height: 1.5;
  background: #f0f6ff;
  border: 1px solid #e2ecf9;
  max-width: 420px;
}
.chat-bubble--reply {
  background: #f8faff;
  border-color: #bdd0f5;
  color: #3b6fd4;
  align-self: flex-start;
}
.status-card {
  background: #f8faff;
  border: 1px solid #e2ecf9;
  border-radius: 12px;
  padding: 28px 24px;
  text-align: center;
  width: 180px;
}
.status-icon  { font-size: 2rem; display: block; margin-bottom: 10px; }
.status-label { font-size: 1rem; font-weight: 700; margin: 0 0 8px; }
.status-text  { font-size: 0.78rem; color: #94a3b8; margin: 0; line-height: 1.5; }
</style>