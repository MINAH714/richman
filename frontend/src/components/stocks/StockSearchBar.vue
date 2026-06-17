<!-- src/components/stocks/StockSearchBar.vue -->
<template>
  <div class="search-wrap" ref="wrapRef">

    <!-- 검색 입력창 -->
    <div class="search-input-row">
      <span class="search-icon">🔍</span>
      <input
        ref="inputRef"
        v-model="query"
        type="text"
        placeholder="종목명 또는 티커 입력 (예: AAPL, 삼성전자)"
        class="search-input"
        @input="handleInput"
        @keydown.down.prevent="moveFocus(1)"
        @keydown.up.prevent="moveFocus(-1)"
        @keydown.enter.prevent="selectFocused"
        @keydown.esc="closeDropdown"
        @focus="onFocus"
        autocomplete="off"
      />
      <!-- 입력값 지우기 버튼 -->
      <button v-if="query" class="btn-clear" @click="clearQuery">✕</button>
    </div>

    <!-- 드롭다운 (자동완성 목록 or 최근 검색) -->
    <div v-if="showDropdown" class="dropdown">

      <!-- 검색 중 로딩 표시 -->
      <div v-if="isLoading" class="dropdown-status">검색 중...</div>

      <!-- 검색 결과 목록 -->
      <template v-else-if="results.length > 0">
        <div class="dropdown-section-label">검색 결과</div>
        <div
          v-for="(item, idx) in results"
          :key="item.symbol"
          :class="['dropdown-item', { focused: focusedIdx === idx }]"
          @mousedown.prevent="selectItem(item)"
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

      <!-- 검색했지만 결과 없음 -->
      <div v-else-if="query.length >= 2 && !isLoading" class="dropdown-status">
        검색 결과가 없습니다.
      </div>

      <!-- 최근 검색 종목 (입력 없을 때) -->
      <template v-else-if="query.length < 2 && recentList.length > 0">
        <div class="dropdown-section-label">
          최근 검색
          <button class="btn-clear-history" @click.stop="clearHistory">전체 삭제</button>
        </div>
        <div
          v-for="(item, idx) in recentList"
          :key="item.symbol + '-recent'"
          :class="['dropdown-item', { focused: focusedIdx === idx }]"
          @mousedown.prevent="selectItem(item)"
          @mouseover="focusedIdx = idx"
        >
          <div class="item-left">
            <span class="item-symbol">🕐 {{ item.symbol }}</span>
          </div>
          <div class="item-right">
            <span class="item-name">{{ item.name }}</span>
            <span class="item-market">{{ item.market }}</span>
          </div>
        </div>
      </template>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { searchStocks } from '@/api/stocks'

const router = useRouter()

// ── 상태 ─────────────────────────────────────────────
const query      = ref('')         // 입력창 텍스트
const results    = ref([])         // 검색 결과 목록
const isLoading  = ref(false)      // 검색 중 여부
const showDropdown = ref(false)    // 드롭다운 표시 여부
const focusedIdx = ref(-1)         // 키보드로 선택 중인 항목 인덱스
const wrapRef    = ref(null)       // 컴포넌트 루트 엘리먼트 ref
const inputRef   = ref(null)       // input 엘리먼트 ref

// ── 로컬스토리지 최근 검색 ────────────────────────────
const STORAGE_KEY = 'stock_recent_searches'
const MAX_RECENT  = 5   // 최대 저장 개수

// 로컬스토리지에서 최근 검색 목록 불러오기
const recentList = ref(
  JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
)

// 최근 검색에 종목 추가 (중복 제거 + 최대 5개 유지)
function addToRecent(item) {
  // 이미 있으면 제거 후 맨 앞에 추가 (가장 최근 순)
  const filtered = recentList.value.filter(r => r.symbol !== item.symbol)
  recentList.value = [item, ...filtered].slice(0, MAX_RECENT)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(recentList.value))
}

// 최근 검색 전체 삭제
function clearHistory() {
  recentList.value = []
  localStorage.removeItem(STORAGE_KEY)
}

// ── 디바운스 처리 ─────────────────────────────────────
// 디바운스(debounce) = 타이핑 중에 매 글자마다 API를 부르면
// 서버에 과부하가 걸리므로, 타이핑을 멈춘 후 300ms 뒤에만 API 호출
let debounceTimer = null

function handleInput() {
  focusedIdx.value = -1
  clearTimeout(debounceTimer)

  if (query.value.length < 2) {
    results.value = []
    showDropdown.value = true   // 최근 검색 표시를 위해 열어둠
    return
  }

  isLoading.value = true
  showDropdown.value = true

  debounceTimer = setTimeout(async () => {
    try {
      const res = await searchStocks(query.value)
      results.value = res.data
    } catch (e) {
      results.value = []
    } finally {
      isLoading.value = false
    }
  }, 300)   // 300ms 대기
}

// ── 드롭다운 열기/닫기 ────────────────────────────────
function onFocus() {
  showDropdown.value = true
}

function closeDropdown() {
  showDropdown.value = false
  focusedIdx.value = -1
}

// 컴포넌트 바깥 클릭 시 드롭다운 닫기
function handleOutsideClick(e) {
  if (wrapRef.value && !wrapRef.value.contains(e.target)) {
    closeDropdown()
  }
}

onMounted(() => {
  document.addEventListener('mousedown', handleOutsideClick)
})
onBeforeUnmount(() => {
  document.removeEventListener('mousedown', handleOutsideClick)
})

// ── 키보드 탐색 ───────────────────────────────────────
const currentList = computed(() =>
  query.value.length >= 2 ? results.value : recentList.value
)

function moveFocus(direction) {
  const len = currentList.value.length
  if (len === 0) return
  // 위아래 방향키로 항목 선택
  focusedIdx.value = (focusedIdx.value + direction + len) % len
}

function selectFocused() {
  if (focusedIdx.value >= 0 && currentList.value[focusedIdx.value]) {
    selectItem(currentList.value[focusedIdx.value])
  }
}

// ── 종목 선택 ─────────────────────────────────────────
function selectItem(item) {
  // 최근 검색에 저장
  addToRecent(item)
  // 입력창 초기화 & 드롭다운 닫기
  query.value = ''
  closeDropdown()
  // 차트 페이지로 이동
  router.push({ name: 'stock-chart', params: { symbol: item.symbol } })
}

// 입력창 초기화 버튼
function clearQuery() {
  query.value = ''
  results.value = []
  inputRef.value?.focus()
}
</script>

<style scoped>
.search-wrap {
  position: relative;
  width: 100%;
  max-width: 520px;
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
.search-icon { font-size: 15px; color: #aaa; }
.search-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 11px 0;
  font-size: 14px;
  background: transparent;
}
.btn-clear {
  background: none;
  border: none;
  color: #aaa;
  cursor: pointer;
  font-size: 14px;
  padding: 4px;
}
.btn-clear:hover { color: #555; }

/* 드롭다운 */
.dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  z-index: 200;
  overflow: hidden;
  max-height: 360px;
  overflow-y: auto;
}
.dropdown-section-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 14px;
  font-size: 11px;
  color: #94a3b8;
  font-weight: 600;
  letter-spacing: 0.05em;
  background: #f8fafc;
}
.btn-clear-history {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 11px;
  cursor: pointer;
}
.btn-clear-history:hover { color: #ef4444; }
.dropdown-status {
  padding: 20px;
  text-align: center;
  color: #aaa;
  font-size: 13px;
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
.item-left {
  display: flex;
  align-items: center;
  gap: 6px;
}
.item-symbol {
  font-weight: 700;
  font-size: 14px;
  color: #1e293b;
}
.item-type {
  font-size: 10px;
  background: #e8f0fe;
  color: #2563eb;
  padding: 1px 6px;
  border-radius: 99px;
}
.item-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}
.item-name {
  font-size: 12px;
  color: #475569;
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.item-market {
  font-size: 11px;
  color: #94a3b8;
}
</style>