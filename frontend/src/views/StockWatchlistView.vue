<!-- src/views/StockWatchlistView.vue -->
<template>
  <div class="dashboard">

    <!-- ── 검색바 섹션 ─────────────────────────────────── -->
    <div class="search-section">
      <StockSearchBar />
    </div>

    <!-- ── 즐겨찾기(관심 종목) 카드 섹션 ─────────────── -->
    <section class="favorites-section">
      <h2 class="section-title">⭐ 관심 종목</h2>

      <!-- 종목 추가 폼 -->
      <div class="add-form">
        <input v-model="newSymbol" placeholder="티커 (예: AAPL)" @keyup.enter="handleAdd" />
        <input v-model="newName"   placeholder="종목명 (예: Apple)" />
        <input v-model="newMarket" placeholder="거래소 (예: NASDAQ)" />
        <button @click="handleAdd" :disabled="!canAdd">+ 추가</button>
      </div>
      <p v-if="addError" class="error-msg">{{ addError }}</p>

      <p v-if="store.items.length === 0 && !store.isLoading" class="empty-msg">
        관심 종목이 없습니다. 위 입력창에서 종목을 추가해보세요!
      </p>

      <!-- 관심 종목 카드 그리드 (크립토 fav-grid와 동일한 구조) -->
      <div v-else class="fav-grid">
        <div
          v-for="item in store.items"
          :key="item.id"
          class="fav-card"
          @click="goToChart(item.symbol)"
        >
          <div class="fav-card-header">
            <span class="coin-kor">{{ item.name }}</span>
            <button
              class="star-btn active"
              @click.stop="handleDelete(item.id)"
              title="관심 종목 삭제"
            >★</button>
          </div>
          <div class="fav-card-market">{{ item.symbol }} · {{ item.market }}</div>
          <div class="fav-card-price">
            {{ item.current_price != null
              ? item.current_price.toLocaleString('ko-KR')
              : '로딩 중...' }}
          </div>
          <!-- 포트폴리오 수익률 (입력한 경우만 표시) -->
          <div
            v-if="item.profit_rate != null"
            class="fav-card-rate"
            :class="item.profit_rate >= 0 ? 'up' : 'down'"
          >
            {{ item.profit_rate >= 0 ? '+' : '' }}{{ item.profit_rate }}%
          </div>
          <div v-else class="fav-card-rate flat">
            <button
              class="btn-portfolio-mini"
              @click.stop="openPortfolioModal(item)"
            >+ 수익률 입력</button>
          </div>
        </div>
      </div>
    </section>

    <hr class="divider" />

    <!-- ── 전체 종목 테이블 (크립토와 동일한 구조) ──────── -->
    <section>
      <div class="toolbar">
        <h2 class="section-title" style="margin:0">
          📋 내 종목 목록 ({{ store.filteredItems.length }})
        </h2>
        <input
          v-model="store.searchQuery"
          type="text"
          placeholder="종목명, 티커 검색..."
          class="search-input"
        />
        <!-- 마지막 갱신 시각 표시 -->
        <span class="last-updated">🔄 10초마다 자동 갱신</span>
      </div>

      <div v-if="store.isLoading && !store.initialLoaded" class="loading">
        불러오는 중...
      </div>

      <table v-else-if="store.filteredItems.length > 0" class="coin-table">
        <thead>
          <tr>
            <th>종목명</th>
            <th>티커</th>
            <th>거래소</th>
            <th>현재가</th>
            <th>수익률</th>
            <th>보유수량</th>
            <th>평균매입가</th>
            <th>포트폴리오</th>
            <th>차트</th>
            <th>삭제</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="item in store.filteredItems"
            :key="item.id"
            class="coin-row"
            @click="goToChart(item.symbol)"
          >
            <td class="name-cell">
              <span class="kor">{{ item.name }}</span>
            </td>
            <td class="market-code">{{ item.symbol }}</td>
            <td class="market-code">{{ item.market }}</td>
            <td class="price">
              {{ item.current_price != null
                ? item.current_price.toLocaleString('ko-KR')
                : '-' }}
            </td>
            <td
              class="rate"
              :class="item.profit_rate != null
                ? (item.profit_rate >= 0 ? 'up' : 'down')
                : 'flat'"
            >
              {{ item.profit_rate != null
                ? (item.profit_rate >= 0 ? '+' : '') + item.profit_rate + '%'
                : '-' }}
            </td>
            <td class="volume">{{ item.quantity ?? '-' }}</td>
            <td class="volume">
              {{ item.average_price != null
                ? Number(item.average_price).toLocaleString('ko-KR')
                : '-' }}
            </td>
            <td>
              <button
                class="btn-table-action"
                @click.stop="openPortfolioModal(item)"
              >
                {{ item.average_price ? '수정' : '+ 입력' }}
              </button>
            </td>
            <td>
              <button
                class="btn-table-action"
                @click.stop="goToChart(item.symbol)"
              >📊 차트</button>
            </td>
            <td>
              <button
                class="btn-del"
                @click.stop="handleDelete(item.id)"
              >✕</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else-if="!store.isLoading" class="loading">
        표시할 종목이 없습니다.
      </div>
    </section>

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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useWatchlistStore } from '@/stores/watchlist'
import StockSearchBar   from '@/components/stocks/StockSearchBar.vue'
import WatchlistCard    from '@/components/stocks/WatchlistCard.vue'
import PortfolioModal   from '@/components/stocks/PortfolioModal.vue'

const store  = useWatchlistStore()
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
    newSymbol.value = ''
    newName.value   = ''
    newMarket.value = ''
    // 추가 후 대시보드 새로고침
    await store.loadDashboard()
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
const modalTarget = ref(null)

function openPortfolioModal(item) {
  modalTarget.value = item
}

async function handlePortfolioSave({ watchlistId, data }) {
  const result = await store.savePortfolio(watchlistId, data)
  if (result.success) {
    modalTarget.value = null
    await store.loadDashboard()
  }
}

// ── 차트 이동 ─────────────────────────────────────────
function goToChart(symbol) {
  router.push({ name: 'stock-chart', params: { symbol } })
}

// ── 폴링 시작/종료 (크립토와 동일한 패턴) ─────────────
onMounted(() => {
  store.startPolling()
})

onUnmounted(() => {
  store.stopPolling()
})
</script>

<style scoped>
/* 크립토 대시보드와 동일한 스타일 구조 */
.dashboard { padding: 1.5rem; max-width: 1200px; margin: 0 auto; }
.section-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 0.75rem; }
.divider { border: none; border-top: 1px solid #e5e7eb; margin: 1.5rem 0; }
.search-section { margin-bottom: 1.5rem; }

/* 종목 추가 폼 */
.add-form {
  display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px;
}
.add-form input {
  flex: 1; min-width: 140px; padding: 8px 12px;
  border: 1px solid #d1d5db; border-radius: 8px; font-size: 13px;
}
.add-form button {
  padding: 8px 16px; background: #2563eb; color: #fff;
  border: none; border-radius: 8px; cursor: pointer;
  font-weight: 600; white-space: nowrap;
}
.add-form button:disabled { background: #aaa; cursor: not-allowed; }
.error-msg { color: #ef4444; font-size: 13px; margin-bottom: 8px; }
.empty-msg { color: #9ca3af; font-size: 0.9rem; padding: 0.5rem 0; }

/* 관심 종목 카드 (크립토 fav-card와 동일) */
.fav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
}
.fav-card {
  border: 1px solid #e5e7eb; border-radius: 10px;
  padding: 0.875rem; cursor: pointer;
  transition: box-shadow 0.15s;
}
.fav-card:hover { box-shadow: 0 2px 10px rgba(0,0,0,0.08); }
.fav-card-header {
  display: flex; justify-content: space-between; align-items: center;
}
.coin-kor { font-weight: 600; font-size: 0.9rem;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  max-width: 100px;
}
.fav-card-market { font-size: 0.72rem; color: #9ca3af; margin-top: 0.2rem; }
.fav-card-price  { font-size: 1rem; font-weight: 600; margin-top: 0.5rem; }
.fav-card-rate   { font-size: 0.85rem; margin-top: 0.15rem; }
.btn-portfolio-mini {
  font-size: 11px; color: #2563eb; background: none;
  border: none; cursor: pointer; padding: 0;
}

/* 툴바 */
.toolbar {
  display: flex; align-items: center; gap: 0.75rem;
  margin-bottom: 1rem; flex-wrap: wrap;
}
.search-input {
  flex: 1; max-width: 300px; padding: 0.5rem 0.875rem;
  border: 1px solid #d1d5db; border-radius: 8px;
  font-size: 0.9rem; outline: none;
}
.search-input:focus { border-color: #2563eb; box-shadow: 0 0 0 2px #2563eb20; }
.last-updated { font-size: 12px; color: #9ca3af; margin-left: auto; }

/* 테이블 (크립토 coin-table과 동일) */
.coin-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.coin-table th {
  text-align: left; padding: 0.5rem 0.75rem;
  border-bottom: 2px solid #e5e7eb;
  color: #6b7280; font-weight: 500; white-space: nowrap;
}
.coin-row { cursor: pointer; }
.coin-row:hover { background: #f9fafb; }
.coin-row td { padding: 0.5rem 0.75rem; border-bottom: 1px solid #f3f4f6; }
.name-cell { display: flex; flex-direction: column; }
.kor { font-weight: 500; }
.market-code { color: #6b7280; font-size: 0.8rem; }
.price  { font-weight: 600; text-align: right; }
.rate   { text-align: right; font-weight: 500; }
.volume { text-align: right; color: #6b7280; }

/* 크립토와 동일한 색상 */
.up   { color: #ef4444; }
.down { color: #3b82f6; }
.flat { color: #6b7280; }

.star-btn {
  background: none; border: none; cursor: pointer;
  font-size: 1.1rem; color: #f59e0b; padding: 0; line-height: 1;
}
.star-btn:hover { color: #ef4444; }

.btn-table-action {
  padding: 4px 10px; font-size: 12px;
  border: 1px solid #ddd; border-radius: 6px;
  background: #fff; cursor: pointer; white-space: nowrap;
}
.btn-table-action:hover { background: #f0f6ff; color: #2563eb; }
.btn-del {
  background: none; border: none;
  color: #ccc; cursor: pointer; font-size: 14px;
}
.btn-del:hover { color: #ef4444; }
.loading { color: #9ca3af; padding: 2rem 0; text-align: center; }
</style>