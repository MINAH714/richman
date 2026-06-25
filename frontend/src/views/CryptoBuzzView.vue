<!-- frontend/src/views/CryptoBuzzView.vue -->
<template>
  <div class="buzz-container">

    <!-- ── 헤더 ───────────────────────────────────────────── -->
    <header class="buzz-header">
      <button class="back-btn" @click="$router.push('/crypto')">← BACK</button>
      <div class="header-title">
        <h1>📡 Social Buzz</h1>
        <span class="subtitle">뉴스 빈도 + 거래량 기반 실시간 버즈 지표</span>
      </div>
      <div class="last-updated" v-if="lastUpdated">
        마지막 갱신: {{ lastUpdated }}
      </div>
    </header>

    <!-- ── 로딩 프로그레스 ────────────────────────────────── -->
    <div v-if="isLoading" class="loading-section">
      <div class="progress-info">
        <span class="progress-coin">
          {{ currentCoin ? `📡 ${currentCoin} 분석 중...` : '데이터 준비 중...' }}
        </span>
        <span class="progress-count">{{ current }} / {{ total }}</span>
      </div>
      <div class="progress-bar-bg">
        <div
          class="progress-bar-fill"
          :style="{ width: progressPct + '%' }"
        />
      </div>
      <div class="progress-pct">{{ progressPct }}%</div>

      <!-- 이미 받은 결과 미리 보여주기 -->
      <div v-if="buzzList.length > 0" class="preview-label">
        분석 완료된 코인 미리보기 ↓
      </div>
    </div>

    <!-- ── 에러 ───────────────────────────────────────────── -->
    <div v-if="error" class="error-msg">{{ error }}</div>

    <!-- ── Buzz 카드 목록 ─────────────────────────────────── -->
    <div class="buzz-grid" v-if="buzzList.length > 0">
      <div
        v-for="(item, index) in sortedBuzzList"
        :key="item.coin_symbol"
        class="buzz-card"
        :class="{ surge: item.is_volume_surge }"
      >
        <!-- 순위 + 코인명 -->
        <div class="card-top">
          <span class="rank">#{{ index + 1 }}</span>
          <div class="coin-info">
            <span class="coin-name">{{ item.korean_name }}</span>
            <span class="coin-symbol">{{ item.coin_symbol }}</span>
          </div>
          <span v-if="item.is_volume_surge" class="surge-badge">🚨 급등</span>
          <span class="grade">{{ item.grade }}</span>
        </div>

        <!-- Buzz 점수 바 -->
        <div class="score-section">
          <div class="score-label">
            <span>Buzz 점수</span>
            <span class="score-value">{{ item.buzz_score }}점</span>
          </div>
          <div class="score-bar-bg">
            <div
              class="score-bar-fill"
              :style="{ width: item.buzz_score + '%' }"
              :class="barClass(item.buzz_score)"
            />
          </div>
        </div>

        <!-- 상세 점수 -->
        <div class="score-detail">
          <div class="detail-item">
            <span class="detail-label">📰 뉴스 점수</span>
            <span class="detail-value">{{ item.news_score }}점</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">📈 거래량 보너스</span>
            <span class="detail-value bonus" :class="{ active: item.volume_bonus > 0 }">
              +{{ item.volume_bonus }}점
            </span>
          </div>
          <div class="detail-item">
            <span class="detail-label">📄 뉴스 기사 수</span>
            <span class="detail-value">{{ item.news_count.toLocaleString() }}건</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">💰 거래대금(24h)</span>
            <span class="detail-value">{{ formatVolume(item.volume_24h) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ── 자동 갱신 안내 ─────────────────────────────────── -->
    <div v-if="!isLoading" class="refresh-info">
      ⏱ 10분마다 자동 갱신 · 다음 갱신까지 <strong>{{ countdown }}초</strong>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const isLoading = ref(false)
const error = ref(null)
const buzzList = ref([])
const lastUpdated = ref('')
const countdown = ref(600)
const current = ref(0)
const total = ref(0)
const currentCoin = ref('')

const progressPct = computed(() =>
  total.value > 0 ? Math.round((current.value / total.value) * 100) : 0
)

const sortedBuzzList = computed(() =>
  [...buzzList.value].sort((a, b) => b.buzz_score - a.buzz_score)
)

let pollingTimer = null
let countdownTimer = null
let eventSource = null

function fetchBuzzStream() {
  // 초기화
  isLoading.value = true
  error.value = null
  buzzList.value = []
  current.value = 0
  total.value = 0
  currentCoin.value = ''

  // 기존 SSE 연결 종료
  if (eventSource) eventSource.close()

  eventSource = new EventSource('http://127.0.0.1:8000/api/crypto/buzz/stream/')

  eventSource.onmessage = (e) => {
    const data = JSON.parse(e.data)

    if (data.type === 'total') {
      total.value = data.total

    } else if (data.type === 'progress') {
      current.value = data.current
      currentCoin.value = data.coin

    } else if (data.type === 'result') {
      // 결과 실시간 추가
      buzzList.value.push(data)

    } else if (data.type === 'done') {
      isLoading.value = false
      lastUpdated.value = new Date().toLocaleTimeString('ko-KR')
      countdown.value = 600
      eventSource.close()
    }
  }

  eventSource.onerror = () => {
    error.value = 'Buzz 데이터를 불러오지 못했습니다.'
    isLoading.value = false
    eventSource.close()
  }
}

onMounted(() => {
  fetchBuzzStream()

  // 10분마다 자동 갱신
  pollingTimer = setInterval(fetchBuzzStream, 600_000)

  // 카운트다운
  countdownTimer = setInterval(() => {
    if (countdown.value > 0) countdown.value--
  }, 1000)
})

onUnmounted(() => {
  clearInterval(pollingTimer)
  clearInterval(countdownTimer)
  if (eventSource) eventSource.close()
})

function formatVolume(vol) {
  if (vol == null) return '-'
  if (vol >= 1_000_000_000_000) return (vol / 1_000_000_000_000).toFixed(1) + '조'
  if (vol >= 100_000_000) return (vol / 100_000_000).toFixed(1) + '억'
  return vol.toLocaleString('ko-KR')
}

function barClass(score) {
  if (score >= 70) return 'high'
  if (score >= 40) return 'mid'
  return 'low'
}
</script>

<style scoped>
.buzz-container {
  min-height: 100vh;
  background: #f0f6ff;
  padding: 1.5rem;
  font-family: 'IBM Plex Mono', monospace;
}

.buzz-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.back-btn {
  padding: 8px 16px;
  background: white;
  border: 1px solid #d0e2f5;
  border-radius: 4px;
  cursor: pointer;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.85rem;
}
.back-btn:hover { background: #e8f0fe; }
.header-title { flex: 1; }
.header-title h1 { margin: 0; font-size: 1.4rem; }
.subtitle { font-size: 0.8rem; color: #6b7280; }
.last-updated { font-size: 0.8rem; color: #9ca3af; }

/* 로딩 프로그레스 */
.loading-section {
  background: white;
  border: 1px solid #e2ecf9;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}
.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  font-size: 0.9rem;
}
.progress-coin { color: #6366f1; font-weight: 500; }
.progress-count { color: #9ca3af; }
.progress-bar-bg {
  height: 10px;
  background: #e2ecf9;
  border-radius: 5px;
  overflow: hidden;
  margin-bottom: 0.4rem;
}
.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  border-radius: 5px;
  transition: width 0.4s ease;
}
.progress-pct {
  text-align: right;
  font-size: 0.8rem;
  color: #6366f1;
  font-weight: 600;
}
.preview-label {
  margin-top: 1rem;
  font-size: 0.8rem;
  color: #9ca3af;
  text-align: center;
}

/* 그리드 */
.buzz-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

/* 카드 */
.buzz-card {
  background: white;
  border: 1px solid #e2ecf9;
  border-radius: 12px;
  padding: 1.25rem;
  transition: box-shadow 0.15s;
  animation: fadeIn 0.3s ease;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
.buzz-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
.buzz-card.surge {
  border-color: #fca5a5;
  background: #fff8f8;
}

.card-top {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}
.rank { font-size: 1.2rem; font-weight: 700; color: #6b7280; min-width: 32px; }
.coin-info { flex: 1; }
.coin-name { font-weight: 600; font-size: 1rem; display: block; }
.coin-symbol { font-size: 0.75rem; color: #9ca3af; }

.surge-badge {
  padding: 2px 8px;
  background: #fee2e2;
  color: #dc2626;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  animation: pulse 1.5s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
.grade { font-size: 1.2rem; }

/* 점수 바 */
.score-section { margin-bottom: 1rem; }
.score-label {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #6b7280;
  margin-bottom: 0.4rem;
}
.score-value { font-weight: 700; color: #0f172a; }
.score-bar-bg {
  height: 8px;
  background: #e2ecf9;
  border-radius: 4px;
  overflow: hidden;
}
.score-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.6s ease;
}
.score-bar-fill.high { background: #ef4444; }
.score-bar-fill.mid  { background: #f59e0b; }
.score-bar-fill.low  { background: #6366f1; }

/* 상세 */
.score-detail {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  border-top: 1px solid #f1f5f9;
  padding-top: 0.75rem;
}
.detail-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.82rem;
}
.detail-label { color: #9ca3af; }
.detail-value { font-weight: 500; }
.detail-value.bonus { color: #d1d5db; }
.detail-value.bonus.active { color: #ef4444; font-weight: 700; }

/* 갱신 */
.refresh-info {
  text-align: center;
  font-size: 0.82rem;
  color: #9ca3af;
  padding: 1rem 0;
}

.error-msg {
  text-align: center;
  padding: 2rem;
  color: #ef4444;
}
</style>