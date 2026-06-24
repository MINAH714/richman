<!-- src/views/StockPredictionView.vue -->
<template>
  <div class="prediction-page">

    <!-- 헤더 -->
    <div class="page-header">
      <h1>🤖 AI 주가 예측</h1>
      <p class="subtitle">이동평균 기반 다음 거래일 예측 결과를 확인하세요.</p>
      <div class="disclaimer-banner">
        ⚠️ 이 예측은 참고용 정보이며, 투자 권유가 아닙니다.
        예측 결과로 인한 투자 손실에 대한 책임을 지지 않습니다.
      </div>
    </div>

    <!-- ── 검색창 (종목명 또는 티커 검색) ── -->
    <div class="search-wrap" ref="searchWrapRef">
      <div class="search-input-row">
        <span class="search-icon">🔍</span>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="종목명 또는 티커 입력 (예: 삼성전자, AAPL)"
          class="search-input"
          @input="handleSearchInput"
          @keydown.down.prevent="moveFocus(1)"
          @keydown.up.prevent="moveFocus(-1)"
          @keydown.enter.prevent="selectFocused"
          @keydown.esc="closeDropdown"
          @focus="showDropdown = true"
          autocomplete="off"
        />
        <button v-if="searchQuery" class="btn-clear-input" @click="clearSearch">✕</button>
      </div>

      <!-- 자동완성 드롭다운 -->
      <div v-if="showDropdown && (searchResults.length > 0 || isSearching)" class="dropdown">
        <div v-if="isSearching" class="dropdown-status">검색 중...</div>
        <template v-else>
          <div class="dropdown-section-label">검색 결과</div>
          <div
            v-for="(item, idx) in searchResults"
            :key="item.symbol"
            :class="['dropdown-item', { focused: focusedIdx === idx }]"
            @mousedown.prevent="selectSearchItem(item)"
            @mouseover="focusedIdx = idx"
          >
            <div class="item-left">
              <span class="item-symbol">{{ item.symbol }}</span>
              <span class="item-type">{{ item.type }}</span>
            </div>
            <div class="item-right">
              <span class="item-name">{{ item.name }}</span>
              <span class="item-market">{{ item.market }}</span>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- 선택된 종목 표시 + 예측 실행 버튼 -->
    <div v-if="selectedStock" class="selected-stock-bar">
      <div class="selected-info">
        <span class="selected-symbol">{{ selectedStock.symbol }}</span>
        <span class="selected-name">{{ selectedStock.name }}</span>
        <span class="selected-market">{{ selectedStock.market }}</span>
      </div>
      <div class="selected-actions">
        <button class="btn-cancel-select" @click="clearSelected">✕ 취소</button>
        <button
          class="btn-predict"
          @click="handlePredict"
          :disabled="isPredicting"
        >
          {{ isPredicting ? '예측 중...' : '🔮 예측 실행' }}
        </button>
      </div>
    </div>

    <p v-if="predictError" class="error-msg">{{ predictError }}</p>

    <!-- ── 관심 종목 카드 섹션 ── -->
    <div v-if="watchlistStore.items.length > 0" class="watchlist-predict-section">
      <h2 class="section-title">⭐ 관심 종목 예측</h2>
      <div class="watchlist-predict-grid">
        <div
          v-for="item in watchlistStore.items"
          :key="item.id"
          class="watchlist-predict-card"
        >
          <div class="wcard-header">
            <span class="wcard-name">{{ item.name }}</span>
            <span class="wcard-market">{{ item.market }}</span>
          </div>
          <div class="wcard-symbol">{{ item.symbol }}</div>
          <div class="wcard-price">
            {{ item.current_price != null
                ? item.current_price.toLocaleString('ko-KR')
                : '가격 정보 없음' }}
          </div>
          <button
            class="btn-predict-card"
            @click="handlePredictDirect(item.symbol, item.name)"
            :disabled="isPredicting && predictingSymbol === item.symbol"
          >
            {{ isPredicting && predictingSymbol === item.symbol
                ? '예측 중...'
                : '🔮 예측 실행' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── 최신 예측 결과 카드 ── -->
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
      <div class="ai-comment">
        <span class="comment-label">🤖 AI 코멘트</span>
        <p>{{ latestResult.ai_comment }}</p>
      </div>
    </div>

    <!-- ── 예측 히스토리 테이블 ── -->
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
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { predictStock, getPredictionHistory, deletePrediction, searchStocks } from '@/api/stocks'
import { useWatchlistStore } from '@/stores/watchlist'

const watchlistStore = useWatchlistStore()

// ── 검색 상태 ─────────────────────────────────────────
const searchQuery   = ref('')
const searchResults = ref([])
const isSearching   = ref(false)
const showDropdown  = ref(false)
const focusedIdx    = ref(-1)
const searchWrapRef = ref(null)
const selectedStock = ref(null)   // 검색으로 선택된 종목

// ── 예측 상태 ─────────────────────────────────────────
const isPredicting     = ref(false)
const predictingSymbol = ref('')   // 카드에서 예측 중인 종목 구분용
const predictError     = ref('')
const latestResult     = ref(null)
const history          = ref([])
const isLoading        = ref(false)

// ── 검색 디바운스 ─────────────────────────────────────
let debounceTimer = null

function handleSearchInput() {
  focusedIdx.value = -1
  clearTimeout(debounceTimer)

  if (searchQuery.value.trim().length < 2) {
    searchResults.value = []
    return
  }

  isSearching.value = true
  showDropdown.value = true

  debounceTimer = setTimeout(async () => {
    try {
      const res = await searchStocks(searchQuery.value.trim())
      searchResults.value = res.data
    } catch (e) {
      searchResults.value = []
    } finally {
      isSearching.value = false
    }
  }, 300)
}

// ── 키보드 탐색 ───────────────────────────────────────
function moveFocus(dir) {
  const len = searchResults.value.length
  if (!len) return
  focusedIdx.value = (focusedIdx.value + dir + len) % len
}

function selectFocused() {
  if (focusedIdx.value >= 0 && searchResults.value[focusedIdx.value]) {
    selectSearchItem(searchResults.value[focusedIdx.value])
  }
}

// ── 검색 결과 선택 ────────────────────────────────────
function selectSearchItem(item) {
  selectedStock.value = item
  searchQuery.value   = `${item.name} (${item.symbol})`
  showDropdown.value  = false
  focusedIdx.value    = -1
}

function closeDropdown() {
  showDropdown.value = false
  focusedIdx.value   = -1
}

function clearSearch() {
  searchQuery.value   = ''
  searchResults.value = []
  selectedStock.value = null
  showDropdown.value  = false
}

function clearSelected() {
  selectedStock.value = null
  searchQuery.value   = ''
  searchResults.value = []
}

// 외부 클릭 시 드롭다운 닫기
function handleOutsideClick(e) {
  if (searchWrapRef.value && !searchWrapRef.value.contains(e.target)) {
    closeDropdown()
  }
}

// ── 예측 실행 (검색창에서) ────────────────────────────
async function handlePredict() {
  if (!selectedStock.value) return
  isPredicting.value     = true
  predictingSymbol.value = selectedStock.value.symbol
  predictError.value     = ''

  try {
    const res = await predictStock(
      selectedStock.value.symbol,
      selectedStock.value.name
    )
    latestResult.value = res.data
    await loadHistory()
    clearSelected()
  } catch (err) {
    predictError.value = err.response?.data?.error || '예측에 실패했습니다.'
  } finally {
    isPredicting.value     = false
    predictingSymbol.value = ''
  }
}

// ── 예측 실행 (관심 종목 카드에서) ───────────────────
async function handlePredictDirect(symbol, name) {
  isPredicting.value     = true
  predictingSymbol.value = symbol
  predictError.value     = ''

  try {
    const res = await predictStock(symbol, name)
    latestResult.value = res.data
    await loadHistory()
  } catch (err) {
    predictError.value = err.response?.data?.error || '예측에 실패했습니다.'
  } finally {
    isPredicting.value     = false
    predictingSymbol.value = ''
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

// ── 정확도 요약 ───────────────────────────────────────
const accuracySummary = computed(() => {
  const completed = history.value.filter(item => item.error_rate != null)
  if (completed.length === 0) return null

  const mae = (
    completed.reduce((sum, item) => sum + Math.abs(item.error_rate), 0)
    / completed.length
  ).toFixed(2)

  const success     = completed.filter(item => Math.abs(item.error_rate) <= 2).length
  const successRate = ((success / completed.length) * 100).toFixed(1)

  return { mae, successRate, total: history.value.length }
})

// ── 라이프사이클 ──────────────────────────────────────
onMounted(() => {
  loadHistory()
  watchlistStore.fetchWatchlist()   // 관심 종목 카드용
  document.addEventListener('mousedown', handleOutsideClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', handleOutsideClick)
})
</script>

<style scoped>
.prediction-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 20px;
  font-family: var(--font-main, 'IBM Plex Mono', monospace);
}

/* 헤더 */
.page-header   { margin-bottom: 24px; }
.page-header h1 { font-size: 26px; font-weight: 700; margin: 0 0 6px; }
.subtitle      { color: #888; font-size: 14px; margin-bottom: 12px; }
.disclaimer-banner {
  background: #fff7ed; border: 1px solid #fed7aa;
  border-radius: 8px; padding: 10px 16px;
  font-size: 13px; color: #c2410c;
}

/* ── 검색창 ── */
.search-wrap {
  position: relative;
  margin-bottom: 12px;
}
.search-input-row {
  display: flex;
  align-items: center;
  background: #fff;
  border: 1.5px solid #dde6f5;
  border-radius: 10px;
  padding: 0 12px;
  gap: 8px;
  transition: border-color 0.15s;
}
.search-input-row:focus-within {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37,99,235,0.1);
}
.search-icon  { font-size: 15px; color: #aaa; }
.search-input {
  flex: 1; border: none; outline: none;
  padding: 12px 0; font-size: 14px; background: transparent;
}
.btn-clear-input {
  background: none; border: none;
  color: #aaa; cursor: pointer; font-size: 14px; padding: 4px;
}
.btn-clear-input:hover { color: #555; }

/* 드롭다운 */
.dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0; right: 0;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  z-index: 200;
  max-height: 320px;
  overflow-y: auto;
}
.dropdown-section-label {
  padding: 8px 14px;
  font-size: 11px;
  color: #94a3b8;
  font-weight: 600;
  background: #f8fafc;
}
.dropdown-status {
  padding: 20px; text-align: center;
  color: #aaa; font-size: 13px;
}
.dropdown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  cursor: pointer;
  transition: background 0.1s;
}
.dropdown-item:hover,
.dropdown-item.focused { background: #f0f6ff; }
.item-left  { display: flex; align-items: center; gap: 6px; }
.item-symbol { font-weight: 700; font-size: 14px; color: #1e293b; }
.item-type {
  font-size: 10px; background: #e8f0fe; color: #2563eb;
  padding: 1px 6px; border-radius: 99px;
}
.item-right { display: flex; flex-direction: column; align-items: flex-end; gap: 2px; }
.item-name  { font-size: 12px; color: #475569; max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.item-market { font-size: 11px; color: #94a3b8; }

/* 선택된 종목 바 */
.selected-stock-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #eff6ff;
  border: 1.5px solid #2563eb;
  border-radius: 10px;
  padding: 12px 16px;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 10px;
}
.selected-info  { display: flex; align-items: center; gap: 10px; }
.selected-symbol { font-size: 16px; font-weight: 700; color: #1e40af; }
.selected-name   { font-size: 14px; color: #374151; }
.selected-market {
  font-size: 11px; background: #dbeafe; color: #2563eb;
  padding: 2px 8px; border-radius: 99px;
}
.selected-actions { display: flex; gap: 8px; }
.btn-cancel-select {
  padding: 8px 14px; border: 1px solid #ddd;
  border-radius: 8px; background: #fff;
  font-size: 13px; cursor: pointer; color: #888;
}
.btn-cancel-select:hover { color: #ef4444; border-color: #ef4444; }

/* 예측 실행 버튼 */
.btn-predict {
  padding: 10px 24px; background: #2563eb; color: #fff;
  border: none; border-radius: 8px; cursor: pointer;
  font-weight: 700; white-space: nowrap; font-size: 14px;
}
.btn-predict:disabled { background: #aaa; cursor: not-allowed; }

.error-msg { color: #ef4444; font-size: 13px; margin-bottom: 12px; }

/* ── 관심 종목 예측 카드 섹션 ── */
.watchlist-predict-section { margin-bottom: 28px; }
.section-title {
  font-size: 16px; font-weight: 700;
  margin: 0 0 14px; color: #1e293b;
}
.watchlist-predict-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}
.watchlist-predict-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition: box-shadow 0.15s, border-color 0.15s;
}
.watchlist-predict-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  border-color: #2563eb;
}
.wcard-header { display: flex; justify-content: space-between; align-items: flex-start; }
.wcard-name   { font-size: 14px; font-weight: 700; color: #1e293b; }
.wcard-market {
  font-size: 10px; background: #f1f5f9; color: #64748b;
  padding: 2px 6px; border-radius: 99px;
}
.wcard-symbol { font-size: 12px; color: #94a3b8; }
.wcard-price  { font-size: 15px; font-weight: 600; color: #1e293b; margin: 4px 0; }
.btn-predict-card {
  width: 100%;
  margin-top: 4px;
  padding: 8px 0;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-predict-card:hover:not(:disabled) { background: #1d4ed8; }
.btn-predict-card:disabled { background: #aaa; cursor: not-allowed; }

/* ── 최신 예측 결과 카드 ── */
.latest-card {
  background: #fff; border-radius: 12px; padding: 24px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.09); margin-bottom: 28px;
}
.latest-header { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }
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
.ai-comment    { background: #f8fafc; border-radius: 8px; padding: 14px; }
.comment-label { font-size: 12px; color: #64748b; font-weight: 600; }
.ai-comment p  { margin: 6px 0 0; font-size: 14px; color: #374151; line-height: 1.6; }

/* ── 히스토리 테이블 ── */
.history-section  { background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.07); }
.history-header   { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.history-header h2 { font-size: 18px; font-weight: 700; margin: 0; }
.btn-refresh {
  padding: 6px 14px; border: 1px solid #ddd;
  border-radius: 8px; background: #fff; cursor: pointer; font-size: 13px;
}
.btn-refresh:hover { background: #f8fafc; }
.status-box { text-align: center; padding: 40px; color: #aaa; }
.history-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.history-table th {
  text-align: left; padding: 10px 12px;
  border-bottom: 2px solid #e2e8f0; color: #64748b; font-size: 12px;
}
.history-table td { padding: 10px 12px; border-bottom: 1px solid #f1f5f9; }
.sym { font-weight: 700; margin-right: 6px; }
.nm  { font-size: 12px; color: #888; }
.badge { padding: 2px 8px; border-radius: 99px; font-size: 12px; font-weight: 600; }
.badge-good    { background: #d1fae5; color: #065f46; }
.badge-bad     { background: #fee2e2; color: #991b1b; }
.badge-pending { background: #f1f5f9; color: #94a3b8; }
.btn-del { background: none; border: none; color: #ccc; cursor: pointer; font-size: 14px; }
.btn-del:hover { color: #ef4444; }

/* ── 정확도 요약 ── */
.accuracy-summary {
  display: flex; gap: 24px; flex-wrap: wrap;
  margin-top: 20px; padding-top: 20px;
  border-top: 1px solid #f1f5f9;
}
.acc-item  { display: flex; flex-direction: column; gap: 4px; }
.acc-label { font-size: 12px; color: #999; }
.acc-value { font-size: 20px; font-weight: 700; color: #2563eb; }
</style>