<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <div class="header-left">
        <span class="header-logo">◈ RICHMAN</span>
        <span class="header-divider">|</span>
        <span class="header-market">KRW MARKET</span>
        <span class="live-badge">
          <span class="live-dot" :class="{ active: isPolling }"></span>
          LIVE
        </span>
      </div>
      <div class="header-right">
        <span class="header-time">{{ currentTime }}</span>
        <button class="sync-btn" @click="handleSync" :disabled="isSyncing">
          <span class="sync-icon" :class="{ spinning: isSyncing }">⟳</span>
          {{ isSyncing ? 'SYNCING...' : 'SYNC' }}
        </button>
      </div>
    </header>

    <div class="summary-bar">
      <div class="summary-item">
        <span class="summary-label">상장 코인</span>
        <span class="summary-value">{{ coins.length }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">상승</span>
        <span class="summary-value green">{{ riseCount }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">하락</span>
        <span class="summary-value red">{{ fallCount }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">보합</span>
        <span class="summary-value muted">{{ evenCount }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">즐겨찾기</span>
        <span class="summary-value accent">{{ favoriteIds.size }}</span>
      </div>
    </div>

    <div class="control-bar">
      <div class="search-wrap">
        <span class="search-icon">⌕</span>
        <input
          v-model="searchQuery"
          class="search-input"
          placeholder="코인명 또는 심볼 검색..."
          @input="currentPage = 1"
        />
        <button v-if="searchQuery" class="clear-btn" @click="searchQuery = ''; currentPage = 1">✕</button>
      </div>

      <div class="filter-tabs">
        <button
          v-for="tab in filterTabs"
          :key="tab.value"
          class="tab-btn"
          :class="{ active: activeFilter === tab.value }"
          @click="activeFilter = tab.value; currentPage = 1"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="sort-wrap">
        <select v-model="sortKey" class="sort-select">
          <option value="acc_trade_price_24h">거래대금순</option>
          <option value="trade_price">현재가순</option>
          <option value="change_rate">변동률순</option>
          <option value="name">이름순</option>
        </select>
        <button class="sort-dir-btn" @click="toggleSortDir">
          {{ sortDir === 'desc' ? '↓' : '↑' }}
        </button>
      </div>
    </div>

    <div v-if="isLoading && coins.length === 0" class="loading-state">
      <div class="loading-grid">
        <div v-for="n in 12" :key="n" class="skeleton-card"></div>
      </div>
    </div>

    <div v-else-if="error" class="error-state">
      <span class="error-icon">⚠</span>
      <p>{{ error }}</p>
      <button @click="fetchCoins" class="retry-btn">재시도</button>
    </div>

    <div v-else class="table-wrap">
      <table class="coin-table">
        <thead>
          <tr>
            <th class="th-fav"></th>
            <th class="th-rank">#</th>
            <th class="th-name">코인</th>
            <th class="th-price" @click="setSort('trade_price')">
              현재가 <span class="sort-arrow" v-if="sortKey === 'trade_price'">{{ sortDir === 'desc' ? '↓' : '↑' }}</span>
            </th>
            <th class="th-change" @click="setSort('change_rate')">
              변동률 <span class="sort-arrow" v-if="sortKey === 'change_rate'">{{ sortDir === 'desc' ? '↓' : '↑' }}</span>
            </th>
            <th class="th-change-price">변동금액</th>
            <th class="th-volume" @click="setSort('acc_trade_price_24h')">
              거래대금(24H) <span class="sort-arrow" v-if="sortKey === 'acc_trade_price_24h'">{{ sortDir === 'desc' ? '↓' : '↑' }}</span>
            </th>
            <th class="th-high">고가</th>
            <th class="th-low">저가</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(coin, index) in paginatedCoins"
            :key="coin.market"
            class="coin-row"
            :class="[
              getChangeClass(coin.change),
              { 'flash-up': flashMap[coin.market] === 'up', 'flash-down': flashMap[coin.market] === 'down' }
            ]"
            @click="goToDetail(coin.market)"
          >
            <td class="td-fav" @click.stop="toggleFavorite(coin)">
              <span class="fav-star" :class="{ active: favoriteIds.has(coin.id) }">
                {{ favoriteIds.has(coin.id) ? '★' : '☆' }}
              </span>
            </td>

            <td class="td-rank">
              {{ (currentPage - 1) * pageSize + index + 1 }}
            </td>

            <td class="td-name">
              <div class="coin-info">
                <span class="coin-symbol">{{ getSymbol(coin.market) }}</span>
                <span class="coin-name-kr">{{ coin.name }}</span>
              </div>
              <span class="coin-market-badge">{{ coin.market }}</span>
            </td>

            <td class="td-price">
              <span class="price-value">{{ formatPrice(coin.trade_price) }}</span>
              <span class="price-unit">₩</span>
            </td>

            <td class="td-change">
              <div class="change-badge" :class="getChangeClass(coin.change)">
                <span class="change-arrow">{{ getChangeArrow(coin.change) }}</span>
                <span class="change-rate">{{ formatChangeRate(coin.change_rate) }}</span>
              </div>
            </td>

            <td class="td-change-price">
              <span :class="getChangeClass(coin.change)">
                {{ coin.change === 'RISE' ? '+' : coin.change === 'FALL' ? '-' : '' }}{{ formatPrice(Math.abs(coin.signed_change_price)) }}
              </span>
            </td>

            <td class="td-volume">
              {{ formatVolume(coin.acc_trade_price_24h) }}
            </td>

            <td class="td-high">
              <span class="high-price">{{ formatPrice(coin.high_price) }}</span>
            </td>

            <td class="td-low">
              <span class="low-price">{{ formatPrice(coin.low_price) }}</span>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="filteredCoins.length === 0" class="empty-state">
        <span>검색 결과가 없습니다</span>
      </div>
    </div>

    <div v-if="totalPages > 1" class="pagination">
      <button class="page-btn" @click="currentPage = 1" :disabled="currentPage === 1">«</button>
      <button class="page-btn" @click="currentPage--" :disabled="currentPage === 1">‹</button>
      <button
        v-for="page in visiblePages"
        :key="page"
        class="page-btn"
        :class="{ active: page === currentPage }"
        @click="currentPage = page"
      >
        {{ page }}
      </button>
      <button class="page-btn" @click="currentPage++" :disabled="currentPage === totalPages">›</button>
      <button class="page-btn" @click="currentPage = totalPages" :disabled="currentPage === totalPages">»</button>
      <span class="page-info">{{ currentPage }} / {{ totalPages }} (총 {{ filteredCoins.length }}개)</span>
    </div>

    <div class="status-bar">
      <span>마지막 갱신: {{ lastUpdated }}</span>
      <span class="dot">·</span>
      <span>10초마다 자동 갱신</span>
      <span class="dot">·</span>
      <span :class="isPolling ? 'green' : 'red'">{{ isPolling ? '● 연결됨' : '○ 중단됨' }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 1. 다시 cryptoAPI 객체를 가져오는 것으로 수정합니다 (i 오타는 수정됨)
import { cryptoAPI } from '@/api/crypto'

const router = useRouter()
const authStore = useAuthStore()

// ── 상태 ──────────────────────────────────────────────
const coins = ref([])
const favorites = ref([])          // [{ id, coin_id, ... }]
const favoriteIds = ref(new Set())  // coin.id 기준 Set

const isLoading = ref(false)
const isSyncing = ref(false)
const error = ref(null)
const isPolling = ref(false)

const searchQuery = ref('')
const activeFilter = ref('all')
const sortKey = ref('acc_trade_price_24h')
const sortDir = ref('desc')

const currentPage = ref(1)
const pageSize = 50

const currentTime = ref('')
const lastUpdated = ref('-')
const flashMap = ref({})   // { 'KRW-BTC': 'up' | 'down' }

let pollingTimer = null
let clockTimer = null

// ── 필터 탭 ───────────────────────────────────────────
const filterTabs = [
  { label: 'ALL', value: 'all' },
  { label: '상승', value: 'RISE' },
  { label: '하락', value: 'FALL' },
  { label: '즐겨찾기', value: 'favorites' },
]

// ── 계산 프로퍼티 ──────────────────────────────────────
const riseCount  = computed(() => coins.value.filter(c => c.change === 'RISE').length)
const fallCount  = computed(() => coins.value.filter(c => c.change === 'FALL').length)
const evenCount  = computed(() => coins.value.filter(c => c.change === 'EVEN').length)

const filteredCoins = computed(() => {
  let list = [...coins.value]

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(c =>
      c.name?.toLowerCase().includes(q) ||
      c.market?.toLowerCase().includes(q)
    )
  }

  if (activeFilter.value === 'RISE') {
    list = list.filter(c => c.change === 'RISE')
  } else if (activeFilter.value === 'FALL') {
    list = list.filter(c => c.change === 'FALL')
  } else if (activeFilter.value === 'favorites') {
    list = list.filter(c => favoriteIds.value.has(c.id))
  }

  list.sort((a, b) => {
    let av = a[sortKey.value] ?? 0
    let bv = b[sortKey.value] ?? 0
    if (sortKey.value === 'name') {
      av = a.name ?? ''
      bv = b.name ?? ''
      return sortDir.value === 'asc' ? av.localeCompare(bv) : bv.localeCompare(av)
    }
    return sortDir.value === 'desc' ? bv - av : av - bv
  })

  return list
})

const totalPages = computed(() => Math.ceil(filteredCoins.value.length / pageSize))

const paginatedCoins = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredCoins.value.slice(start, start + pageSize)
})

const visiblePages = computed(() => {
  const total = totalPages.value
  const cur = currentPage.value
  const pages = []
  const start = Math.max(1, cur - 2)
  const end = Math.min(total, cur + 2)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

async function fetchCoins() {
  try {
    error.value = null
    const prevPrices = {}
    coins.value.forEach(c => { prevPrices[c.market] = c.trade_price })

    const response = await cryptoAPI.getCoins()
    
    // 💡 핵심 수정: 실제 배열 데이터가 어디 있는지 찾아 꺼냅니다.
    // Axios 응답 객체이거나 백엔드에서 { data: [...] } 형태로 보냈을 경우를 모두 커버합니다.
    let data = response
    if (response && response.data) {
      data = response.data
    }

    // data가 정상적인 배열일 때만 forEach 실행
    if (Array.isArray(data)) {
      data.forEach(c => {
        if (prevPrices[c.market] !== undefined && prevPrices[c.market] !== c.trade_price) {
          flashMap.value[c.market] = c.trade_price > prevPrices[c.market] ? 'up' : 'down'
          setTimeout(() => { delete flashMap.value[c.market] }, 600)
        }
      })
      coins.value = data
      lastUpdated.value = new Date().toLocaleTimeString('ko-KR')
    } else {
      // 배열이 아니면 에러를 띄우고 무한 폴링을 중단합니다.
      console.error('API 응답이 배열이 아닙니다. 실제 응답 확인:', response)
      error.value = '데이터 형식이 올바르지 않습니다.'
      stopPolling() 
    }
    
  } catch (e) {
    error.value = '코인 데이터를 불러오지 못했습니다.'
    console.error('fetchCoins 에러:', e)
    stopPolling() // 서버/네트워크 에러 시에도 콘솔 도배 방지를 위해 폴링 중단
  }
}

async function fetchFavorites() {
  if (!authStore.isAuthenticated) return
  try {
    // 3. cryptoAPI. 접두어 추가
    const data = await cryptoAPI.getFavorites()
    favorites.value = data
    favoriteIds.value = new Set(data.map(f => f.coin))
  } catch (e) {
    console.error('즐겨찾기 로드 실패', e)
  }
}

async function toggleFavorite(coin) {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  const isFav = favoriteIds.value.has(coin.id)
  const newSet = new Set(favoriteIds.value)
  
  if (isFav) {
    newSet.delete(coin.id)
    favoriteIds.value = newSet
    try {
      const fav = favorites.value.find(f => f.coin === coin.id)
      // 4. cryptoAPI. 접두어 추가
      if (fav) await cryptoAPI.removeFavorite(fav.id)
    } catch {
      newSet.add(coin.id)
      favoriteIds.value = new Set(newSet)
    }
  } else {
    newSet.add(coin.id)
    favoriteIds.value = newSet
    try {
      // 5. cryptoAPI. 접두어 추가
      const created = await cryptoAPI.addFavorite(coin.id)
      favorites.value.push(created)
    } catch {
      newSet.delete(coin.id)
      favoriteIds.value = new Set(newSet)
    }
  }
}

async function handleSync() {
  if (!authStore.isAuthenticated) { router.push('/login'); return }
  isSyncing.value = true
  try {
    // 6. cryptoAPI. 접두어 추가
    await cryptoAPI.syncMarkets()
    await fetchCoins()
  } catch (e) {
    console.error('동기화 실패', e)
  } finally {
    isSyncing.value = false
  }
}

// ── 폴링 ──────────────────────────────────────────────
function startPolling() {
  isPolling.value = true
  pollingTimer = setInterval(fetchCoins, 10000)
}

function stopPolling() {
  isPolling.value = false
  clearInterval(pollingTimer)
}

// ── 유틸 ──────────────────────────────────────────────
function formatPrice(price) {
  if (price === null || price === undefined) return '-'
  if (price >= 100) return Number(price).toLocaleString('ko-KR', { maximumFractionDigits: 0 })
  if (price >= 1) return Number(price).toLocaleString('ko-KR', { maximumFractionDigits: 2 })
  return Number(price).toLocaleString('ko-KR', { maximumFractionDigits: 6 })
}

function formatChangeRate(rate) {
  if (rate === null || rate === undefined) return '0.00%'
  return (rate * 100).toFixed(2) + '%'
}

function formatVolume(vol) {
  if (!vol) return '-'
  const v = Number(vol)
  if (v >= 1_000_000_000_000) return (v / 1_000_000_000_000).toFixed(2) + '조'
  if (v >= 100_000_000) return (v / 100_000_000).toFixed(0) + '억'
  if (v >= 10_000) return (v / 10_000).toFixed(0) + '만'
  return v.toLocaleString('ko-KR')
}

function getChangeClass(change) {
  if (change === 'RISE') return 'rise'
  if (change === 'FALL') return 'fall'
  return 'even'
}

function getChangeArrow(change) {
  if (change === 'RISE') return '▲'
  if (change === 'FALL') return '▼'
  return '━'
}

function getSymbol(market) {
  return market?.replace('KRW-', '') ?? ''
}

function goToDetail(market) {
  router.push(`/crypto/${market}`)
}

function setSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'desc' ? 'asc' : 'desc'
  } else {
    sortKey.value = key
    sortDir.value = 'desc'
  }
}

function toggleSortDir() {
  sortDir.value = sortDir.value === 'desc' ? 'asc' : 'desc'
}

function updateClock() {
  currentTime.value = new Date().toLocaleTimeString('ko-KR', { hour12: false })
}

// ── 라이프사이클 ───────────────────────────────────────
onMounted(async () => {
  isLoading.value = true
  await Promise.all([fetchCoins(), fetchFavorites()])
  isLoading.value = false
  startPolling()
  updateClock()
  clockTimer = setInterval(updateClock, 1000)
})

onUnmounted(() => {
  stopPolling()
  clearInterval(clockTimer)
})

watch([searchQuery, activeFilter, sortKey, sortDir], () => {
  currentPage.value = 1
})
</script>

<style scoped>
/* ── 폰트 ─────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Noto+Sans+KR:wght@400;500;700&display=swap');

/* ── 변수 ─────────────────────────────────────────── */
:root {
  --bg: #f0f6ff;
  --bg-card: #ffffff;
  --bg-row-hover: #f5f9ff;
  --border: #e2ecf9;
  --border-light: #d0e2f5;

  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #94a3b8;

  --green: #059669;
  --red: #dc2626;
  --blue: #2563eb;
  --yellow: #d97706;
  --accent: #2563eb;

  --font-mono: 'IBM Plex Mono', monospace;
  --font-kr: 'Noto Sans KR', sans-serif;
}

/* ── 전체 레이아웃 ──────────────────────────────────── */
.dashboard {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text-primary);
  font-family: var(--font-mono);
  padding-bottom: 40px;
}

/* ── 헤더 ─────────────────────────────────────────── */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 28px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  letter-spacing: 0.08em;
}

.header-logo {
  font-size: 15px;
  font-weight: 600;
  color: var(--blue);
  letter-spacing: 0.12em;
}

.header-divider {
  color: var(--border-light);
}

.header-market {
  color: var(--text-secondary);
  font-size: 11px;
  letter-spacing: 0.15em;
}

.live-badge {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 10px;
  letter-spacing: 0.15em;
  color: var(--text-muted);
  border: 1px solid var(--border-light);
  padding: 2px 8px;
  border-radius: 2px;
}

.live-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-muted);
}
.live-dot.active {
  background: var(--green);
  box-shadow: 0 0 6px var(--green);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-time {
  font-size: 13px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
  letter-spacing: 0.05em;
}

.sync-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.1em;
  padding: 5px 14px;
  background: transparent;
  border: 1px solid var(--border-light);
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 2px;
  transition: all 0.2s;
}
.sync-btn:hover:not(:disabled) {
  border-color: var(--blue);
  color: var(--blue);
}
.sync-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.sync-icon {
  font-size: 14px;
  display: inline-block;
}
.sync-icon.spinning {
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ── 요약 바 ──────────────────────────────────────── */
.summary-bar {
  display: flex;
  gap: 0;
  border-bottom: 1px solid var(--border);
  background: var(--bg-card);
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 10px 28px;
  border-right: 1px solid var(--border);
}

.summary-label {
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 0.12em;
}

.summary-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}
.summary-value.green { color: var(--green); }
.summary-value.red { color: var(--red); }
.summary-value.muted { color: var(--text-secondary); }
.summary-value.accent { color: var(--accent); }

/* ── 컨트롤 바 ────────────────────────────────────── */
.control-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 20px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  flex-wrap: wrap;
}

.search-wrap {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 200px;
  max-width: 320px;
}

.search-icon {
  position: absolute;
  left: 10px;
  color: var(--text-muted);
  font-size: 16px;
  pointer-events: none;
}

.search-input {
  width: 100%;
  background: var(--bg);
  border: 1px solid var(--border-light);
  color: var(--text-primary);
  font-family: var(--font-mono);
  font-size: 12px;
  padding: 7px 32px 7px 30px;
  border-radius: 2px;
  outline: none;
  letter-spacing: 0.03em;
  transition: border-color 0.2s;
}
.search-input::placeholder {
  color: var(--text-muted);
}
.search-input:focus {
  border-color: var(--accent);
}

.clear-btn {
  position: absolute;
  right: 8px;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 12px;
  padding: 0;
  line-height: 1;
}
.clear-btn:hover { color: var(--text-primary); }

.filter-tabs {
  display: flex;
  gap: 4px;
}

.tab-btn {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.08em;
  padding: 5px 14px;
  background: transparent;
  border: 1px solid var(--border-light);
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 2px;
  transition: all 0.15s;
}
.tab-btn:hover { color: var(--text-secondary); border-color: var(--border-light); }
.tab-btn.active {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}

.sort-wrap {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: auto;
}

.sort-select {
  font-family: var(--font-mono);
  font-size: 11px;
  background: var(--bg);
  border: 1px solid var(--border-light);
  color: var(--text-secondary);
  padding: 5px 8px;
  border-radius: 2px;
  outline: none;
  cursor: pointer;
}

.sort-dir-btn {
  font-size: 16px;
  background: transparent;
  border: 1px solid var(--border-light);
  color: var(--text-secondary);
  width: 30px;
  height: 30px;
  cursor: pointer;
  border-radius: 2px;
  transition: all 0.15s;
}
.sort-dir-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
}

/* ── 테이블 ───────────────────────────────────────── */
.table-wrap {
  overflow-x: auto;
}

.coin-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

thead tr {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
}

th {
  padding: 10px 14px;
  text-align: right;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  white-space: nowrap;
  cursor: pointer;
  user-select: none;
}
th:first-child,
th:nth-child(2),
th:nth-child(3) {
  text-align: left;
}
th:hover { color: var(--text-secondary); }

.sort-arrow {
  color: var(--accent);
  margin-left: 3px;
}

.coin-row {
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  transition: background 0.1s;
}
.coin-row:hover {
  background: var(--bg-row-hover);
}

/* 플래시 효과 */
@keyframes flashUp {
  0%   { background: rgba(5, 150, 105, 0.13); }
  100% { background: transparent; }
}
@keyframes flashDown {
  0%   { background: rgba(220, 38, 38, 0.10); }
  100% { background: transparent; }
}
.coin-row.flash-up  { animation: flashUp 0.6s ease-out; }
.coin-row.flash-down { animation: flashDown 0.6s ease-out; }

td {
  padding: 10px 14px;
  text-align: right;
  white-space: nowrap;
  vertical-align: middle;
}
td:nth-child(3) { text-align: left; }

/* 즐겨찾기 */
.th-fav, .td-fav {
  width: 36px;
  text-align: center !important;
  padding: 10px 6px;
}

.fav-star {
  font-size: 14px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s;
  line-height: 1;
}
.fav-star:hover { color: var(--yellow); transform: scale(1.2); }
.fav-star.active { color: var(--yellow); }

/* 순위 */
.td-rank {
  color: var(--text-muted);
  font-size: 11px;
  text-align: left !important;
  width: 40px;
}

/* 코인명 */
.td-name { text-align: left !important; min-width: 140px; }
.coin-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.coin-symbol {
  font-family: var(--font-mono);
  font-weight: 600;
  font-size: 13px;
  color: var(--text-primary);
  letter-spacing: 0.05em;
}
.coin-name-kr {
  font-family: var(--font-kr);
  font-size: 10px;
  color: var(--text-muted);
}
.coin-market-badge {
  font-size: 9px;
  color: var(--text-muted);
  letter-spacing: 0.08em;
  display: none;
}

/* 가격 */
.price-value {
  font-family: var(--font-mono);
  font-weight: 500;
  font-size: 13px;
}
.price-unit {
  font-size: 10px;
  color: var(--text-muted);
  margin-left: 2px;
}

/* 변동률 */
.change-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 2px;
  font-size: 11px;
  font-weight: 600;
}
.change-arrow { font-size: 9px; }

/* 색상 클래스 */
.rise .change-badge,
.td-change .rise {
  background: rgba(5, 150, 105, 0.10);
  color: var(--green);
}
.fall .change-badge,
.td-change .fall {
  background: rgba(220, 38, 38, 0.10);
  color: var(--red);
}
.even .change-badge {
  background: rgba(100, 116, 139, 0.08);
  color: var(--text-secondary);
}

.rise { color: var(--green); }
.fall { color: var(--red); }
.even { color: var(--text-secondary); }

.high-price { color: var(--red); }
.low-price  { color: var(--blue); }

/* ── 로딩 스켈레톤 ────────────────────────────────── */
.loading-state {
  padding: 20px;
}
.loading-grid {
  display: grid;
  gap: 2px;
}
.skeleton-card {
  height: 44px;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2ecf9 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s ease-in-out infinite;
  border-radius: 1px;
}
@keyframes shimmer {
  0% { background-position: 200% center; }
  100% { background-position: -200% center; }
}

/* ── 에러 / 빈 상태 ───────────────────────────────── */
.error-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px 20px;
  color: var(--text-muted);
  font-size: 13px;
}
.error-icon { font-size: 28px; color: var(--red); }

.retry-btn {
  font-family: var(--font-mono);
  font-size: 11px;
  padding: 6px 18px;
  background: transparent;
  border: 1px solid var(--red);
  color: var(--red);
  cursor: pointer;
  border-radius: 2px;
  letter-spacing: 0.08em;
  transition: all 0.15s;
}
.retry-btn:hover { background: rgba(255,77,106,0.1); }

/* ── 페이지네이션 ─────────────────────────────────── */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 4px;
  padding: 20px;
}

.page-btn {
  font-family: var(--font-mono);
  font-size: 12px;
  min-width: 32px;
  height: 32px;
  background: transparent;
  border: 1px solid var(--border-light);
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 2px;
  transition: all 0.15s;
}
.page-btn:hover:not(:disabled) {
  border-color: var(--accent);
  color: var(--accent);
}
.page-btn.active {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}
.page-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-info {
  margin-left: 8px;
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 0.05em;
}

/* ── 하단 상태 바 ─────────────────────────────────── */
.status-bar {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 8px 24px;
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 0.08em;
  border-top: 1px solid var(--border);
}
.status-bar .dot { color: var(--border-light); }
.status-bar .green { color: var(--green); }
.status-bar .red { color: var(--red); }
</style>