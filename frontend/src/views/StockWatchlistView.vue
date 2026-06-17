<!-- src/views/StockWatchlistView.vue -->
<template>
  <div class="watchlist-page">
    <div class="page-header">
      <h1>📈 관심 종목</h1>
      <p class="subtitle">즐겨찾기한 종목과 포트폴리오를 한눈에 확인하세요.</p>
    </div>

    <div class="search-section">
      <StockSearchBar/>
    </div>

    <!-- 종목 추가 입력 폼 -->
    <div class="add-form">
      <input v-model="newSymbol" placeholder="티커 입력 (예: AAPL, 005930.KS)" @keyup.enter="handleAdd" />
      <input v-model="newName"   placeholder="종목명 (예: Apple, 삼성전자)" />
      <input v-model="newMarket" placeholder="거래소 (예: NASDAQ, KRX)" />
      <button @click="handleAdd" :disabled="!canAdd">+ 추가</button>
    </div>
    <p v-if="addError" class="error-msg">{{ addError }}</p>

    <!-- 로딩 상태 -->
    <div v-if="store.isLoading" class="loading">불러오는 중...</div>

    <!-- 관심 종목 없을 때 -->
    <div v-else-if="store.items.length === 0" class="empty">
      <p>아직 추가된 관심 종목이 없어요.</p>
      <p>위 입력창에서 종목을 추가해 보세요! 🔍</p>
    </div>

    <!-- 관심 종목 카드 목록 -->
    <div v-else class="card-grid">
      <WatchlistCard
        v-for="item in store.items"
        :key="item.id"
        :item="item"
        @delete="handleDelete"
        @edit-portfolio="openPortfolioModal"
        @go-chart="goToChart"
      />
    </div>

    <!-- 포트폴리오 입력 모달 -->
    <PortfolioModal
      v-if="modalTarget"
      :watchlist-id="modalTarget.id"
      :symbol="modalTarget.symbol"
      :name="modalTarget.name"
      :existing="modalTarget.portfolio"
      @close="modalTarget = null"
      @saved="handlePortfolioSave"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useWatchlistStore } from '@/stores/watchlist'
import WatchlistCard from '@/components/stocks/WatchlistCard.vue'
import PortfolioModal from '@/components/stocks/PortfolioModal.vue'
import StockSearchBar from '@/components/stocks/StockSearchBar.vue'

const store = useWatchlistStore()
const router = useRouter()

// ── 관심 종목 추가 폼 ─────────────────────────────────
const newSymbol = ref('')
const newName   = ref('')
const newMarket = ref('')
const addError  = ref('')

const canAdd = computed(() =>
  newSymbol.value.trim() && newName.value.trim() && newMarket.value.trim()
)

async function handleAdd() {
  if (!canAdd.value) return
  addError.value = ''

  const result = await store.addToWatchlist({
    symbol: newSymbol.value.trim().toUpperCase(),
    name:   newName.value.trim(),
    market: newMarket.value.trim().toUpperCase(),
  })

  if (result.success) {
    // 성공하면 입력창 초기화
    newSymbol.value = ''
    newName.value   = ''
    newMarket.value = ''
  } else {
    addError.value = result.message
  }
}

// ── 관심 종목 삭제 ────────────────────────────────────
async function handleDelete(id) {
  if (!confirm('관심 종목에서 삭제할까요?')) return
  await store.removeFromWatchlist(id)
}

// ── 포트폴리오 모달 ───────────────────────────────────
const modalTarget = ref(null)   // 현재 편집 중인 종목 (null이면 모달 닫힘)

function openPortfolioModal(item) {
  modalTarget.value = item
}

async function handlePortfolioSave({ watchlistId, data }) {
  const result = await store.savePortfolio(watchlistId, data)
  if (result.success) {
    modalTarget.value = null   // 저장 성공 시 모달 닫기
    // 수익률 반영을 위해 목록 새로고침
    store.fetchWatchlist()
  }
}

// ── 차트 페이지 이동 (기능 2에서 연결 예정) ───────────
function goToChart(symbol) {
  router.push({ name: 'stock-chart', params: { symbol } })
}

// ── 페이지 진입 시 목록 불러오기 ─────────────────────
onMounted(() => {
  store.fetchWatchlist()
})
</script>

<style scoped>
.watchlist-page { max-width: 1100px; margin: 0 auto; padding: 32px 20px; }
.page-header { margin-bottom: 28px; }
.page-header h1 { font-size: 28px; font-weight: 700; margin: 0 0 6px; }
.subtitle { color: #888; font-size: 14px; }
.add-form {
  display: flex; gap: 8px; flex-wrap: wrap;
  margin-bottom: 8px;
}
.add-form input {
  flex: 1; min-width: 160px; padding: 10px 14px;
  border: 1px solid #ddd; border-radius: 8px; font-size: 14px;
}
.add-form button {
  padding: 10px 20px; background: #2563eb; color: #fff;
  border: none; border-radius: 8px; cursor: pointer; font-weight: 600;
  white-space: nowrap;
}
.add-form button:disabled { background: #aaa; cursor: not-allowed; }
.error-msg { color: #ef4444; font-size: 13px; margin-bottom: 16px; }
.loading { text-align: center; padding: 60px; color: #aaa; }
.empty { text-align: center; padding: 60px; color: #aaa; line-height: 2; }
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 24px;
}
.search-section {
  margin-bottom: 24px;
}
</style>