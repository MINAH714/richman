<template>
  <div class="dashboard">

    <div class="search-section">
      <StockSearchBar />
    </div>

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
            {{
              item.price != null
                ? (
                    item.market === 'KRX'
                      ? item.price.toLocaleString('ko-KR') + '원'
                      : '$' + item.price.toLocaleString('en-US', {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2
                        })
                  )
                : '로딩 중...'
            }}
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

    <section>
      <div class="toolbar">
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

        <div class="refresh-status">
          <span :class="['refresh-dot', { blink: store.isRefreshing }]"></span>
          <span class="refresh-label">10초마다 자동 갱신</span>
        </div>
      </div>

      <div v-if="store.isLoading && store.dashboardItems.length === 0" class="loading">
        주식 데이터를 불러오는 중...
      </div>

      <table v-else class="coin-table">
        <thead>
          <tr>
            <th>종목명</th>
            <th>티커</th>
            <th>거래소</th>
            <th class="text-right">현재가</th>
            <th class="text-right">등락률</th>
            <th class="text-center">관심 종목</th>
            <th class="text-center">포트폴리오 추가</th>
          </tr>
        </thead>
        <tbody>
          <!-- template 부분: tbody의 각 행 -->
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
              {{ item.price != null ? item.price.toLocaleString('ko-KR') : '-' }}
            </td>
            <td class="rate" :class="changeClass(item.change_rate)">
              {{ item.change_rate != null ? (item.change_rate > 0 ? '+' : '') + item.change_rate + '%' : '-' }}
            </td>
            <td class="text-center">
              <button
                :class="['star-btn', { active: item.is_watched }]"
                @click.stop="store.toggleWatchlist(item)"
                :title="item.is_watched ? '관심 종목 해제' : '관심 종목 추가'"
              >
                {{ item.is_watched ? '★' : '☆' }}
              </button>
            </td>
            <td class="text-center" @click.stop>
              <div v-if="addTarget?.symbol !== item.symbol" class="add-cell">
                <button
                  class="btn-add-holding"
                  :disabled="item.price == null"
                  :title="item.price == null ? '현재가 로딩 중' : ''"
                  @click="openAddInput(item)"
                >
                  + 추가
                </button>
              </div>
              <div v-else class="add-input-row">
                <input
                  v-model.number="addQuantity"
                  type="number"
                  min="0.0001"
                  step="0.0001"
                  placeholder="수량"
                  class="qty-input"
                  @keyup.enter="confirmAddHolding(item)"
                />
                <button
                  class="btn-confirm"
                  :disabled="!addQuantity || addQuantity <= 0 || isSubmittingAdd"
                  @click="confirmAddHolding(item)"
                >
                  {{ isSubmittingAdd ? '처리중' : '확인' }}
                </button>
                <button class="btn-cancel-mini" @click="closeAddInput">취소</button>
              </div>
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

// ── 등락 클래스 (change 값을 기준으로 판별하도록 간소화) ──
function changeClass(value) {
  if (!value || value === 0) return 'flat'
  return value > 0 ? 'up' : 'down'
}

// ── 관심종목에 수량과 함께 추가 (마이페이지 포트폴리오 연동) ──
const addTarget = ref(null)       // 현재 수량 입력 중인 종목
const addQuantity = ref(null)
const isSubmittingAdd = ref(false)

function openAddInput(item) {
  addTarget.value = item
  addQuantity.value = null
}

function closeAddInput() {
  addTarget.value = null
  addQuantity.value = null
}

async function confirmAddHolding(item) {
  if (!addQuantity.value || addQuantity.value <= 0) return

  if (item.price == null) {
    alert('현재가를 불러오는 중입니다. 잠시 후 다시 시도해주세요.')
    return
  }

  const submittedQuantity = addQuantity.value   // ⭐ [신규 추가] 리셋 전에 값 보존

  isSubmittingAdd.value = true
  try {
    const result = await store.addHoldingWithQuantity(item, submittedQuantity)
    if (result.success) {
      closeAddInput()
      alert(`${item.name} ${submittedQuantity}개가 포트폴리오에 추가되었습니다.`)   // ⭐ [수정] addQuantity.value → submittedQuantity
      router.push({ name: 'mypage', query: { tab: 'portfolio' } })
    } else {
      alert(result.message || '추가에 실패했습니다.')
    }
  } finally {
    isSubmittingAdd.value = false
  }
}

// ── 라이프사이클: 폴링 제어 ────────────────────────────
onMounted(async () => {
  await store.fetchWatchlist()   // 관심 종목 카드 상단 로드
  await store.startPolling()     // 수정: 데이터 확보 전 공백 방지를 위한 대시보드 기동
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

/* 정렬 헬퍼 클래스 */
.text-right { text-align: right !important; }
.text-center { text-align: center !important; }

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

/* 갱신 피드백 애니메이션 */
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

.loading { color: #9ca3af; padding: 4rem 0; text-align: center; font-size: 0.95rem; }

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
/* style 부분: 기존 .star-btn 관련 스타일 아래에 추가 */
.add-cell { display: flex; justify-content: center; }
.btn-add-holding {
  padding: 4px 12px;
  border: 1px solid #2563eb;
  border-radius: 6px;
  background: #fff;
  color: #2563eb;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s;
}
.btn-add-holding:hover { background: #2563eb; color: #fff; }

.add-input-row {
  display: flex;
  align-items: center;
  gap: 4px;
  justify-content: center;
}
.qty-input {
  width: 64px;
  padding: 4px 6px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.8rem;
}
.btn-confirm {
  padding: 4px 8px;
  border: none;
  border-radius: 6px;
  background: #2563eb;
  color: #fff;
  font-size: 0.75rem;
  cursor: pointer;
  white-space: nowrap;
}
.btn-confirm:disabled { background: #aaa; cursor: not-allowed; }
.btn-cancel-mini {
  padding: 4px 8px;
  border: none;
  border-radius: 6px;
  background: #f1f5f9;
  color: #64748b;
  font-size: 0.75rem;
  cursor: pointer;
}
/* ⭐ [신규 추가] disabled 상태 스타일 */
.btn-add-holding:disabled {
  border-color: #d1d5db;
  color: #9ca3af;
  cursor: not-allowed;
}
.btn-add-holding:disabled:hover { background: #fff; color: #9ca3af; }
</style>