<!-- src/views/StockWatchlistView.vue -->
<template>
  <div class="dashboard">

    <!-- ── 검색바 ───────────────────────────────────────── -->
    <div class="search-section">
      <StockSearchBar />
    </div>

    <!-- ── 관심 종목 카드 섹션 ────────────────────────────── -->
    <section v-if="store.items.length > 0" class="favorites-section">
      <h2 class="section-title">⭐ 관심 종목</h2>
      <div class="fav-grid">
        <div
          v-for="item in store.items"
          :key="item.id"
          class="fav-card"
          @click="goToChart(item.symbol)"
        >
          <div class="fav-card-header">
            <span class="coin-kor">{{ item.name }}</span>
            <button class="star-btn active" @click.stop="handleWatchlistDelete(item.id)">★</button>
          </div>
          <div class="fav-card-market">{{ item.symbol }} · {{ item.market }}</div>
          <div class="fav-card-price">
            {{ item.current_price != null
                ? item.current_price.toLocaleString('ko-KR')
                : '로딩 중...' }}
          </div>
          <div
            v-if="item.profit_rate != null"
            class="fav-card-rate"
            :class="item.profit_rate >= 0 ? 'up' : 'down'"
          >
            {{ item.profit_rate >= 0 ? '+' : '' }}{{ item.profit_rate }}%
          </div>
          <div v-else class="fav-card-rate flat">
            <button class="btn-portfolio-mini" @click.stop="openPortfolioModal(item)">
              + 수익률 입력
            </button>
          </div>
        </div>
      </div>
    </section>

    <hr v-if="store.items.length > 0" class="divider" />

    <!-- ── 대시보드 메인 ──────────────────────────────────── -->
    <section>
      <div class="toolbar">
        <!-- 국내 / 미국 탭 버튼 -->
        <div class="tab-group">
          <button
            :class="['tab-btn', { active: store.activeTab === 'kr' }]"
            @click="store.changeTab('kr')"
          >🇰🇷 국내 주식</button>
          <button
            :class="['tab-btn', { active: store.activeTab === 'us' }]"
            @click="store.changeTab('us')"
          >🇺🇸 미국 주식</button>
        </div>

        <!-- 자동 갱신 상태 표시 -->
        <div class="refresh-status">
          <span :class="['refresh-dot', { blink: store.isRefreshing }]"></span>
          <span class="refresh-label">10초마다 자동 갱신</span>
        </div>
      </div>

      <!-- 로딩 중 -->
      <div v-if="store.isLoading" class="loading">불러오는 중...</div>

      <!-- 종목 테이블 -->
      <table v-else class="coin-table">
        <thead>
          <tr>
            <th>종목명</th>
            <th>티커</th>
            <th>거래소</th>
            <th>현재가</th>
            <th>등락률</th>
            <th>관심 종목</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="item in store.dashboardItems"
            :key="item.symbol"
            class="coin-row"
            :class="{ refreshing: store.isRefreshing }"
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
            <td class="rate" :class="changeClass(item.change_type)">
              {{ item.change_rate != null
                  ? (item.change_rate >= 0 ? '+' : '') + item.change_rate + '%'
                  : '-' }}
            </td>
            <td>
              <button
                :class="['star-btn', { active: item.is_watched }]"
                @click.stop="store.toggleWatchlist(item)"
                :title="item.is_watched ? '관심 종목 해제' : '관심 종목 추가'"
              >
                {{ item.is_watched ? '★' : '☆' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="load-more-wrap">
        <button
          v-if="store.hasMore"
          class="btn-load-more"
          :disabled="store.isLoadingMore"
          @click="store.loadMore()"
        >
          {{ store.isLoadingMore ? '불러오는 중...' : `⬇ 더보기 (${store.dashboardItems.length}개 표시 중)` }}
        </button>
        <p v-else-if="store.dashboardItems.length > 0" class="no-more">
          ✅ 전체 {{ store.dashboardItems.length }}개 종목을 모두 불러왔습니다.
        </p>
      </div>
    </section>

    <!-- 포트폴리오 모달 -->
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
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useWatchlistStore } from '@/stores/watchlist'
import StockSearchBar from '@/components/stocks/StockSearchBar.vue'
import PortfolioModal from '@/components/stocks/PortfolioModal.vue'

const store  = useWatchlistStore()
const router = useRouter()

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

// ── 관심 종목 삭제 ────────────────────────────────────
async function handleWatchlistDelete(id) {
  if (!confirm('관심 종목에서 삭제할까요?')) return
  await store.removeFromWatchlist(id)
}

// ── 차트 이동 ─────────────────────────────────────────
function goToChart(symbol) {
  router.push({ name: 'stock-chart', params: { symbol } })
}

// ── 등락 클래스 ───────────────────────────────────────
function changeClass(type) {
  if (type === 'RISE') return 'up'
  if (type === 'FALL') return 'down'
  return 'flat'
}

// ── 폴링 시작/종료 ────────────────────────────────────
onMounted(async () => {
  await store.fetchWatchlist()   // 관심 종목 카드용
  store.startPolling()           // 대시보드 10초 폴링
})

onUnmounted(() => {
  store.stopPolling()
})
</script>

<style scoped>
.dashboard { padding: 1.5rem; max-width: 1200px; margin: 0 auto; }
.section-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 0.75rem; }
.divider { border: none; border-top: 1px solid #e5e7eb; margin: 1.5rem 0; }
.search-section { margin-bottom: 1.5rem; }

/* 관심 종목 카드 */
.fav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 0.75rem; margin-bottom: 1rem;
}
.fav-card {
  border: 1px solid #e5e7eb; border-radius: 10px;
  padding: 0.875rem; cursor: pointer; transition: box-shadow 0.15s;
}
.fav-card:hover { box-shadow: 0 2px 10px rgba(0,0,0,0.08); }
.fav-card-header { display: flex; justify-content: space-between; align-items: center; }
.coin-kor {
  font-weight: 600; font-size: 0.9rem;
  white-space: nowrap; overflow: hidden;
  text-overflow: ellipsis; max-width: 100px;
}
.fav-card-market { font-size: 0.72rem; color: #9ca3af; margin-top: 0.2rem; }
.fav-card-price  { font-size: 1rem; font-weight: 600; margin-top: 0.5rem; }
.fav-card-rate   { font-size: 0.85rem; margin-top: 0.15rem; }
.btn-portfolio-mini {
  font-size: 11px; color: #2563eb;
  background: none; border: none; cursor: pointer; padding: 0;
}

/* 탭 + 갱신 상태 툴바 */
.toolbar {
  display: flex; align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem; flex-wrap: wrap; gap: 0.75rem;
}
.tab-group { display: flex; gap: 8px; }
.tab-btn {
  padding: 8px 20px; border: 1.5px solid #d1d5db;
  border-radius: 99px; background: #fff;
  font-size: 0.85rem; font-weight: 500;
  cursor: pointer; transition: all 0.15s;
}
.tab-btn:hover { border-color: #2563eb; color: #2563eb; }
.tab-btn.active {
  background: #2563eb; color: #fff;
  border-color: #2563eb; font-weight: 700;
}

/* 자동 갱신 표시 */
.refresh-status {
  display: flex; align-items: center; gap: 6px;
}
.refresh-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #10b981;
  transition: background 0.2s;
}
/* 갱신 시 깜빡임 애니메이션 */
.refresh-dot.blink {
  animation: blink-pulse 0.2s ease-in-out;
}
@keyframes blink-pulse {
  0%   { background: #10b981; transform: scale(1);   }
  50%  { background: #f59e0b; transform: scale(1.6); }
  100% { background: #10b981; transform: scale(1);   }
}
.refresh-label { font-size: 12px; color: #9ca3af; }

/* 테이블 */
.coin-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.coin-table th {
  text-align: left; padding: 0.5rem 0.75rem;
  border-bottom: 2px solid #e5e7eb;
  color: #6b7280; font-weight: 500; white-space: nowrap;
}
.coin-row { cursor: pointer; transition: background 0.1s; }
.coin-row:hover { background: #f9fafb; }
.coin-row td { padding: 0.5rem 0.75rem; border-bottom: 1px solid #f3f4f6; }

/* 갱신 시 행 깜빡임 */
.coin-row.refreshing {
  animation: row-flash 0.2s ease-in-out;
}
@keyframes row-flash {
  0%   { background: transparent; }
  50%  { background: #fefce8; }
  100% { background: transparent; }
}

.name-cell { display: flex; flex-direction: column; }
.kor        { font-weight: 500; }
.market-code { color: #6b7280; font-size: 0.8rem; }
.price  { font-weight: 600; text-align: right; }
.rate   { text-align: right; font-weight: 500; }
.up     { color: #ef4444; }
.down   { color: #3b82f6; }
.flat   { color: #6b7280; }

.star-btn {
  background: none; border: none; cursor: pointer;
  font-size: 1.2rem; color: #d1d5db;
  padding: 0; transition: color 0.15s;
}
.star-btn.active { color: #f59e0b; }
.star-btn:hover  { color: #f59e0b; }

.loading { color: #9ca3af; padding: 2rem 0; text-align: center; }
/* 더보기 버튼 */
.load-more-wrap {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}
.btn-load-more {
  padding: 10px 32px;
  border: 1.5px solid #2563eb;
  border-radius: 99px;
  background: #fff;
  color: #2563eb;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-load-more:hover:not(:disabled) {
  background: #2563eb;
  color: #fff;
}
.btn-load-more:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.no-more {
  font-size: 13px;
  color: #9ca3af;
}
</style>