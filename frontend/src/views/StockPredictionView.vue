<!-- src/views/StockPredictionView.vue -->
<template>
  <div class="prediction-page">

    <!-- 헤더 -->
    <div class="page-header">
      <h1>🤖 AI 주가 예측</h1>
      <p class="subtitle">이동평균 기반 다음 거래일 예측 결과를 확인하세요.</p>
      <!-- 투자 주의 문구 (기획서 필수 요건) -->
      <div class="disclaimer-banner">
        ⚠️ 이 예측은 참고용 정보이며, 투자 권유가 아닙니다.
        예측 결과로 인한 투자 손실에 대한 책임을 지지 않습니다.
      </div>
    </div>

    <!-- 종목 선택 + 예측 실행 -->
    <div class="predict-form">
      <input
        v-model="inputSymbol"
        placeholder="티커 입력 (예: AAPL, 005930.KS)"
        class="predict-input"
        @keyup.enter="handlePredict"
      />
      <input
        v-model="inputName"
        placeholder="종목명 (예: Apple, 삼성전자)"
        class="predict-input"
      />
      <button
        class="btn-predict"
        @click="handlePredict"
        :disabled="isPredicting || !inputSymbol"
      >
        {{ isPredicting ? '예측 중...' : '🔮 예측 실행' }}
      </button>
    </div>

    <p v-if="predictError" class="error-msg">{{ predictError }}</p>

    <!-- 최신 예측 결과 카드 -->
    <div v-if="latestResult" class="latest-card">
      <div class="latest-header">
        <span class="latest-symbol">{{ latestResult.symbol }}</span>
        <span class="latest-name">{{ latestResult.name }}</span>
        <span class="latest-date">예측 대상일: {{ latestResult.predicted_date }}</span>
      </div>
      <div class="latest-body">
        <div class="price-box">
          <span class="price-label">AI 예측가</span>
          <span class="price-value">
            {{ Number(latestResult.predicted_price).toLocaleString() }}
          </span>
        </div>
        <div class="price-box" v-if="latestResult.actual_price">
          <span class="price-label">실제 종가</span>
          <span class="price-value">
            {{ Number(latestResult.actual_price).toLocaleString() }}
          </span>
        </div>
        <div class="price-box" v-if="latestResult.error_rate != null">
          <span class="price-label">예측 오차율</span>
          <span
            class="price-value"
            :class="Math.abs(latestResult.error_rate) <= 2 ? 'good' : 'bad'"
          >
            {{ latestResult.error_rate > 0 ? '+' : '' }}{{ latestResult.error_rate }}%
          </span>
        </div>
        <div v-else class="price-box">
          <span class="price-label">예측 오차율</span>
          <span class="price-value pending">예측일 이후 자동 업데이트</span>
        </div>
      </div>
      <!-- AI 코멘트 -->
      <div class="ai-comment">
        <span class="comment-label">🤖 AI 코멘트</span>
        <p>{{ latestResult.ai_comment }}</p>
      </div>
    </div>

    <!-- 예측 히스토리 테이블 -->
    <div class="history-section">
      <div class="history-header">
        <h2>📋 예측 히스토리</h2>
        <button class="btn-refresh" @click="loadHistory">새로고침</button>
      </div>

      <div v-if="isLoading" class="status-box">불러오는 중...</div>

      <div v-else-if="history.length === 0" class="status-box">
        아직 예측 기록이 없어요. 위에서 종목을 예측해 보세요!
      </div>

      <table v-else class="history-table">
        <thead>
          <tr>
            <th>종목</th>
            <th>예측 대상일</th>
            <th>예측가</th>
            <th>실제 종가</th>
            <th>오차율</th>
            <th>삭제</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in history" :key="item.id">
            <td>
              <span class="sym">{{ item.symbol }}</span>
              <span class="nm">{{ item.name }}</span>
            </td>
            <td>{{ item.predicted_date }}</td>
            <td>{{ Number(item.predicted_price).toLocaleString() }}</td>
            <td>
              {{ item.actual_price
                  ? Number(item.actual_price).toLocaleString()
                  : '—' }}
            </td>
            <td>
              <span
                v-if="item.error_rate != null"
                :class="['badge', Math.abs(item.error_rate) <= 2 ? 'badge-good' : 'badge-bad']"
              >
                {{ item.error_rate > 0 ? '+' : '' }}{{ item.error_rate }}%
              </span>
              <span v-else class="badge badge-pending">대기중</span>
            </td>
            <td>
              <button class="btn-del" @click="handleDelete(item.id)">✕</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 정확도 요약 (실제가가 있는 항목이 1개 이상일 때만 표시) -->
      <div v-if="accuracySummary" class="accuracy-summary">
        <div class="acc-item">
          <span class="acc-label">평균 오차율(MAE 기준)</span>
          <span class="acc-value">{{ accuracySummary.mae }}%</span>
        </div>
        <div class="acc-item">
          <span class="acc-label">예측 성공률 (오차 ±2% 이내)</span>
          <span class="acc-value">{{ accuracySummary.successRate }}%</span>
        </div>
        <div class="acc-item">
          <span class="acc-label">총 예측 횟수</span>
          <span class="acc-value">{{ accuracySummary.total }}회</span>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { predictStock, getPredictionHistory, deletePrediction } from '@/api/stocks'

// ── 상태 ─────────────────────────────────────────────
const inputSymbol  = ref('')
const inputName    = ref('')
const isPredicting = ref(false)
const predictError = ref('')
const latestResult = ref(null)   // 방금 예측한 결과
const history      = ref([])     // 예측 히스토리 목록
const isLoading    = ref(false)

// ── 예측 실행 ─────────────────────────────────────────
async function handlePredict() {
  if (!inputSymbol.value.trim()) return
  isPredicting.value = true
  predictError.value = ''

  try {
    const res = await predictStock(
      inputSymbol.value.trim().toUpperCase(),
      inputName.value.trim() || inputSymbol.value.trim().toUpperCase()
    )
    latestResult.value = res.data
    // 히스토리 새로고침 (방금 예측한 것도 목록에 반영)
    await loadHistory()
    inputSymbol.value = ''
    inputName.value   = ''
  } catch (err) {
    predictError.value = err.response?.data?.error || '예측에 실패했습니다.'
  } finally {
    isPredicting.value = false
  }
}

// ── 히스토리 조회 ─────────────────────────────────────
async function loadHistory() {
  isLoading.value = true
  try {
    const res = await getPredictionHistory()
    history.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

// ── 히스토리 삭제 ─────────────────────────────────────
async function handleDelete(id) {
  if (!confirm('이 예측 기록을 삭제할까요?')) return
  await deletePrediction(id)
  history.value = history.value.filter(item => item.id !== id)
}

// ── 정확도 요약 계산 (computed) ───────────────────────
const accuracySummary = computed(() => {
  // 실제가가 입력된 항목만 추출
  const completed = history.value.filter(
    item => item.error_rate != null
  )
  if (completed.length === 0) return null

  // MAE (평균 절대 오차율)
  const mae = (
    completed.reduce((sum, item) => sum + Math.abs(item.error_rate), 0)
    / completed.length
  ).toFixed(2)

  // 오차 ±2% 이내를 성공으로 판정
  const success = completed.filter(
    item => Math.abs(item.error_rate) <= 2
  ).length
  const successRate = ((success / completed.length) * 100).toFixed(1)

  return { mae, successRate, total: history.value.length }
})

// ── 마운트 시 히스토리 로드 ───────────────────────────
onMounted(loadHistory)
</script>

<style scoped>
.prediction-page { max-width: 900px; margin: 0 auto; padding: 32px 20px; }
.page-header { margin-bottom: 24px; }
.page-header h1 { font-size: 28px; font-weight: 700; margin: 0 0 6px; }
.subtitle { color: #888; font-size: 14px; margin-bottom: 12px; }
.disclaimer-banner {
  background: #fff7ed; border: 1px solid #fed7aa;
  border-radius: 8px; padding: 10px 16px;
  font-size: 13px; color: #c2410c;
}
.predict-form {
  display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 8px;
}
.predict-input {
  flex: 1; min-width: 160px; padding: 10px 14px;
  border: 1px solid #ddd; border-radius: 8px; font-size: 14px;
}
.btn-predict {
  padding: 10px 24px; background: #2563eb; color: #fff;
  border: none; border-radius: 8px; cursor: pointer;
  font-weight: 700; white-space: nowrap;
}
.btn-predict:disabled { background: #aaa; cursor: not-allowed; }
.error-msg { color: #ef4444; font-size: 13px; margin-bottom: 12px; }

/* 최신 예측 결과 카드 */
.latest-card {
  background: #fff; border-radius: 12px; padding: 24px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.09); margin-bottom: 32px;
}
.latest-header {
  display: flex; align-items: center; gap: 10px; margin-bottom: 16px;
}
.latest-symbol { font-size: 20px; font-weight: 700; }
.latest-name   { font-size: 14px; color: #666; }
.latest-date   { margin-left: auto; font-size: 12px; color: #aaa; }
.latest-body   { display: flex; gap: 24px; flex-wrap: wrap; margin-bottom: 16px; }
.price-box     { display: flex; flex-direction: column; gap: 4px; }
.price-label   { font-size: 12px; color: #999; }
.price-value   { font-size: 20px; font-weight: 700; }
.price-value.good    { color: #10b981; }
.price-value.bad     { color: #ef4444; }
.price-value.pending { font-size: 13px; color: #aaa; }

/* AI 코멘트 */
.ai-comment {
  background: #f8fafc; border-radius: 8px; padding: 14px;
}
.comment-label { font-size: 12px; color: #64748b; font-weight: 600; }
.ai-comment p  { margin: 6px 0 0; font-size: 14px; color: #374151; line-height: 1.6; }

/* 히스토리 테이블 */
.history-section  { background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.07); }
.history-header   { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.history-header h2 { font-size: 18px; font-weight: 700; margin: 0; }
.btn-refresh {
  padding: 6px 14px; border: 1px solid #ddd; border-radius: 8px;
  background: #fff; cursor: pointer; font-size: 13px;
}
.status-box { text-align: center; padding: 40px; color: #aaa; }
.history-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.history-table th {
  text-align: left; padding: 10px 12px;
  border-bottom: 2px solid #e2e8f0; color: #64748b; font-size: 12px;
}
.history-table td { padding: 10px 12px; border-bottom: 1px solid #f1f5f9; }
.sym { font-weight: 700; margin-right: 6px; }
.nm  { font-size: 12px; color: #888; }
.badge {
  padding: 2px 8px; border-radius: 99px; font-size: 12px; font-weight: 600;
}
.badge-good    { background: #d1fae5; color: #065f46; }
.badge-bad     { background: #fee2e2; color: #991b1b; }
.badge-pending { background: #f1f5f9; color: #94a3b8; }
.btn-del {
  background: none; border: none; color: #ccc;
  cursor: pointer; font-size: 14px;
}
.btn-del:hover { color: #ef4444; }

/* 정확도 요약 */
.accuracy-summary {
  display: flex; gap: 24px; flex-wrap: wrap;
  margin-top: 20px; padding-top: 20px;
  border-top: 1px solid #f1f5f9;
}
.acc-item  { display: flex; flex-direction: column; gap: 4px; }
.acc-label { font-size: 12px; color: #999; }
.acc-value { font-size: 20px; font-weight: 700; color: #2563eb; }
</style>