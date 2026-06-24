<template>
  <div class="portfolio-tab">
    
    <header class="port-header">
      <div class="breadcrumb">
        <span>Overview</span>
        <i class="ti ti-chevron-right"></i>
        <span class="current">Portfolio</span>
      </div>
      <button class="btn-add" @click="isCashModalOpen = true">
        <i class="ti ti-plus"></i> 현금 자산 추가하기
      </button>
    </header>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
    </div>

    <main v-else class="port-main">
      
      <section class="net-worth-section">
        <span class="section-label">Total Net Worth</span>
        <div class="net-worth-value">
          <h2 class="amount">₩{{ summary.total_assets.toLocaleString() }}</h2>
          <span class="badge-live">실시간</span>
        </div>
        <p class="update-time"><i class="ti ti-refresh"></i> 방금 업데이트됨</p>
      </section>

      <section class="dashboard-grid">
        
        <div class="chart-card card">
          <div class="card-header">
            <h3>자산 비중</h3>
            <i class="ti ti-chart-pie"></i>
          </div>

          <div class="donut-center-wrap">
            <DonutChart
              v-if="assetDonutData.length > 0"
              :categories="assetDonutData"
              :total-expense="summary.total_assets"
              :color-map="assetColorMap"
              center-label="총 자산"
              :size="240"
            />
            <p v-else class="empty-chart-text">등록된 자산이 없습니다.</p>
          </div>
        </div>

        <div class="list-card card">
          <div class="list-header">
            <span class="col-type">자산 분류</span>
            <span class="col-value">평가 금액</span>
          </div>
          <div class="list-body">
            <div class="list-row">
              <div class="asset-info">
                <div class="icon-box"><i class="ti ti-building-bank"></i></div>
                <div class="asset-text">
                  <p class="asset-name">예금 & 적금</p>
                  <p class="asset-count">{{ assets.savings.length }}개의 상품</p>
                </div>
              </div>
              <div class="asset-value-wrap">
                <span class="asset-value">₩{{ totalSavings.toLocaleString() }}</span>
                <i class="ti ti-chevron-right arrow"></i>
              </div>
            </div>

            <div class="list-row">
              <div class="asset-info">
                <div class="icon-box stock-icon"><i class="ti ti-chart-candle"></i></div>
                <div class="asset-text">
                  <p class="asset-name">주식</p>
                  <p class="asset-count">{{ assets.stocks.length }}개의 종목</p>
                </div>
              </div>
              <div class="asset-value-wrap">
                <span class="asset-value">₩{{ totalStocks.toLocaleString() }}</span>
                <i class="ti ti-chevron-right arrow"></i>
              </div>
            </div>

            <div class="list-row">
              <div class="asset-info">
                <div class="icon-box cash-icon"><i class="ti ti-cash"></i></div>
                <div class="asset-text">
                  <p class="asset-name">현금</p>
                  <p class="asset-count">{{ (assets.cash || []).length }}개의 자산</p>
                </div>
              </div>
              <div class="asset-value-wrap">
                <span class="asset-value">₩{{ totalCash.toLocaleString() }}</span>
                <i class="ti ti-chevron-right arrow"></i>
              </div>
            </div>   <!-- ⭐ [신규 추가] -->
          </div>
        </div>
      </section>

      <section class="portfolio-items outer-section-card">
        <div class="section-header">
          <h3>나의 예적금 포트폴리오</h3>
          <router-link to="/finlife" class="link-more">더 둘러보기</router-link>
        </div>

        <div v-if="assets.savings.length === 0" class="empty-state">
          <i class="ti ti-pig-money"></i>
          <p>아직 가입한 예적금 상품이 없습니다.</p>
          <router-link to="/finlife" class="btn-primary">상품 찾아보기</router-link>
        </div>

        <div v-else class="product-grid">
          <div 
            v-for="product in assets.savings" 
            :key="product.id"
            class="product-card-inner"
          >
            <button class="btn-delete-asset" @click.stop="handleDeleteItem(product.id)" title="삭제">✕</button>
            <div class="product-header">
              <div class="icon-box-small"><i class="ti ti-coin"></i></div>
              <span class="bank-badge">{{ product.brokerage }}</span>
            </div>
            
            <div class="product-body">
              <p class="product-name" :title="product.asset_name">{{ product.asset_name }}</p>
              <p class="product-amount">₩{{ Number(product.invested_amount).toLocaleString() }}</p>
              
              <div class="product-rate">
                <i class="ti ti-trending-up"></i>
                <span>최고 연 {{ product.interest_rate }}% 적용</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ⭐ [신규 추가] 나의 주식 포트폴리오 섹션 -->
      <section class="portfolio-items outer-section-card">
        <div class="section-header">
          <h3>나의 주식 포트폴리오</h3>
          <router-link to="/stocks/watchlist" class="link-more">대시보드로 이동</router-link>
        </div>

        <div v-if="assets.stocks.length === 0" class="empty-state">
          <i class="ti ti-chart-candle"></i>
          <p>아직 보유한 주식이 없습니다.</p>
          <router-link to="/stocks/watchlist" class="btn-primary">종목 찾아보기</router-link>
        </div>

        <div v-else class="product-grid">
          <div
            v-for="stock in assets.stocks"
            :key="stock.id"
            class="product-card-inner"
          >
            <button class="btn-delete-asset" @click.stop="handleDeleteItem(stock.id)" title="삭제">✕</button>
            <div class="product-header">
              <div class="icon-box-small stock-icon-small"><i class="ti ti-chart-candle"></i></div>
              <span class="bank-badge stock-badge">{{ stock.brokerage }}</span>
            </div>

            <div class="product-body">
              <p class="product-name" :title="stock.asset_name">{{ stock.asset_name }}</p>
              <p class="product-amount">
                {{ stock.currency === 'USD' ? '$' : '₩' }}{{ Number(stock.invested_amount).toLocaleString() }}
              </p>

              <div class="stock-detail-row">
                <span>보유 수량</span>
                <template v-if="editingStockId === stock.id">
                  <div class="qty-edit-group" @click.stop>
                    <input v-model.number="editQuantity" type="number" min="0.0001" step="0.0001" class="qty-edit-input" @keyup.enter="saveEditQuantity(stock)" />
                    <button class="btn-qty-save" @click="saveEditQuantity(stock)">✓</button>
                    <button class="btn-qty-cancel" @click="cancelEditQuantity">✕</button>
                  </div>
                </template>
                <template v-else>
                  <span class="qty-display" @click.stop="startEditQuantity(stock)">
                    <strong>{{ Number(stock.quantity) }}</strong>
                    <span class="qty-edit-icon">✎</span>
                  </span>
                </template>
              </div>
              <div class="stock-detail-row">
                <span>평균 매입가</span>
                <strong>{{ stock.currency === 'USD' ? '$' : '₩' }}{{ Number(stock.purchase_price).toLocaleString() }}</strong>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- ⭐ [신규 추가] 나의 크립토 포트폴리오 섹션 -->
      <section class="portfolio-items outer-section-card">
        <div class="section-header">
          <h3>나의 크립토 포트폴리오</h3>
          <router-link to="/crypto" class="link-more">대시보드로 이동</router-link>
        </div>

        <div v-if="assets.crypto.length === 0" class="empty-state">
          <i class="ti ti-coin"></i>
          <p>아직 보유한 코인이 없습니다.</p>
          <router-link to="/crypto" class="btn-primary">코인 찾아보기</router-link>
        </div>

        <div v-else class="product-grid">
          <div
            v-for="coin in assets.crypto"
            :key="coin.id"
            class="product-card-inner"
          >
            <button class="btn-delete-asset" @click.stop="handleDeleteItem(coin.id)" title="삭제">✕</button>
            <div class="product-header">
              <div class="icon-box-small crypto-icon-small"><i class="ti ti-coin"></i></div>
              <span class="bank-badge crypto-badge">{{ coin.brokerage }}</span>
            </div>

            <div class="product-body">
              <p class="product-name" :title="coin.asset_name">{{ coin.asset_name }}</p>
              <p class="product-amount">₩{{ Number(coin.invested_amount).toLocaleString() }}</p>

              <div class="stock-detail-row">
                <span>보유 수량</span>
                <strong>{{ Number(coin.quantity) }}</strong>
              </div>
              <div class="stock-detail-row">
                <span>평균 매입가</span>
                <strong>₩{{ Number(coin.purchase_price).toLocaleString() }}</strong>
              </div>
            </div>
          </div>
        </div>
      </section>

    <!-- ⭐ [신규 추가] 현금 자산 추가 모달 -->
      <div v-if="isCashModalOpen" class="modal-backdrop" @click.self="closeCashModal">
        <div class="modal-box">
          <h3>현금 자산 추가</h3>
          <p class="modal-symbol">비상금, 현금 보관액 등을 등록하세요</p>

          <div class="form-group">
            <label>자산 이름</label>
            <input
              v-model="cashForm.asset_name"
              type="text"
              placeholder="예: 비상금, 현금 보관액"
            />
          </div>

          <div class="form-group">
            <label>금액 (원)</label>
            <input
              v-model.number="cashForm.amount"
              type="number"
              min="0"
              step="1"
              placeholder="예: 1000000"
            />
          </div>

          <div class="form-group">
            <label>메모 (선택)</label>
            <input
              v-model="cashForm.memo"
              type="text"
              placeholder="예: 급할 때 쓸 돈"
            />
          </div>
          <div class="modal-actions">
            <button class="btn-cancel" @click="closeCashModal">취소</button>
            <button class="btn-save" :disabled="!isCashFormValid" @click="submitCashHolding">저장</button>
          </div>
        </div>
      </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from '@/api/axios'
import { deletePortfolioItem, updateStockQuantity, addCashHolding } from '@/api/portfolio'   // ⭐ [수정]
import DonutChart from '@/components/consumption/DonutChart.vue'   


const isLoading = ref(true)

const summary = ref({ total_assets: 0 })
const assets = ref({
  savings: [],
  stocks: [],
  crypto: [],
  cash: [],
})

const totalSavings = computed(() => {
  return assets.value.savings.reduce((acc, curr) => acc + Number(curr.invested_amount), 0)
})

// ⭐ [신규 추가] 주식 자산 총액 + 자산 비중(%) 계산
const totalStocks = computed(() => {
  return assets.value.stocks.reduce((acc, curr) => acc + Number(curr.invested_amount), 0)
})

const savingsRatio = computed(() => {
  const total = summary.value.total_assets
  if (!total || total === 0) return 0
  return Math.round((totalSavings.value / total) * 100)
})

const stocksRatio = computed(() => {
  const total = summary.value.total_assets
  if (!total || total === 0) return 0
  return Math.round((totalStocks.value / total) * 100)
})

const totalCrypto = computed(() => {
  return assets.value.crypto.reduce((acc, curr) => acc + Number(curr.invested_amount), 0)
})

const cryptoRatio = computed(() => {
  const total = summary.value.total_assets
  if (!total || total === 0) return 0
  return Math.round((totalCrypto.value / total) * 100)
})

const totalCash = computed(() => {
  return (assets.value.cash || []).reduce((acc, curr) => acc + Number(curr.invested_amount), 0)
})

const cashRatio = computed(() => {
  const total = summary.value.total_assets
  if (!total || total === 0) return 0
  return Math.round((totalCash.value / total) * 100)
})

async function fetchPortfolio() {
  try {
    const response = await axios.get('/api/portfolio/my/')
    summary.value = response.data.summary
    assets.value = response.data.assets
  } catch (error) {
    console.error("포트폴리오 정보를 불러오는데 실패했습니다.", error)
  } finally {
    isLoading.value = false
  }
}

async function handleDeleteItem(id) {
  if (!confirm('이 자산을 포트폴리오에서 삭제할까요?')) return
  try {
    await deletePortfolioItem(id)
    await fetchPortfolio()   // 삭제 후 목록 다시 불러오기
  } catch (err) {
    console.error('자산 삭제 실패:', err)
    alert('삭제에 실패했습니다.')
  }
}

// ⭐ [신규 추가] 주식 카드 보유수량 수정 모드 토글 및 처리
const editingStockId = ref(null)   // 현재 수량 수정 중인 주식 카드 id
const editQuantity = ref(null)

function startEditQuantity(stock) {
  editingStockId.value = stock.id
  editQuantity.value = Number(stock.quantity)
}

function cancelEditQuantity() {
  editingStockId.value = null
  editQuantity.value = null
}

async function saveEditQuantity(stock) {
  if (!editQuantity.value || editQuantity.value <= 0) {
    alert('수량은 0보다 커야 합니다.')
    return
  }
  try {
    await updateStockQuantity(stock.id, editQuantity.value)
    cancelEditQuantity()
    await fetchPortfolio()   // 수정 후 목록 갱신
  } catch (err) {
    console.error('수량 수정 실패:', err)
    alert('수량 수정에 실패했습니다.')
  }
}

// 기존 saveEditQuantity 함수 아래에 추가

const assetColorMap = {
  savings: '#2563eb',   // 예적금 - 파랑
  stocks:  '#ef4444',   // 주식 - 빨강
  cash:    '#10b981',   // 현금 - 초록
  crypto:  '#f59e0b',   // 크립토 - 주황
}

const assetDonutData = computed(() => {
  const total = summary.value.total_assets
  if (!total || total === 0) return []

  const rows = [
    { category: 'savings', category_display: '예적금', amount: totalSavings.value },
    { category: 'stocks',  category_display: '주식',   amount: totalStocks.value },
    { category: 'crypto',  category_display: '크립토', amount: totalCrypto.value },
    { category: 'cash',    category_display: '현금',   amount: totalCash.value },
  ]

  return rows
    .filter(r => r.amount > 0)
    .map(r => ({
      ...r,
      ratio: Math.round((r.amount / total) * 100),
    }))
})

// ⭐ [신규 추가] 현금 자산 추가 모달 상태 및 처리
const isCashModalOpen = ref(false)
const cashForm = ref({ asset_name: '', amount: null, memo: '' })

const isCashFormValid = computed(() =>
  cashForm.value.asset_name.trim().length > 0 && cashForm.value.amount > 0
)

function closeCashModal() {
  isCashModalOpen.value = false
  cashForm.value = { asset_name: '', amount: null, memo: '' }
}

async function submitCashHolding() {
  if (!isCashFormValid.value) return
  try {
    await addCashHolding({
      asset_name: cashForm.value.asset_name.trim(),
      amount: cashForm.value.amount,
      memo: cashForm.value.memo,
    })
    closeCashModal()
    await fetchPortfolio()
  } catch (err) {
    console.error('현금 자산 추가 실패:', err)
    alert('현금 자산 추가에 실패했습니다.')
  }
}




onMounted(() => {
  fetchPortfolio()
})

</script>



<style scoped>
/* ── 전체 래퍼 ── */
.portfolio-tab {
  font-family: var(--font-main, 'Noto Sans KR', sans-serif);
  color: var(--color-text-primary, #334155);
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ── 헤더 ── */
.port-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--color-border, #e2e8f0);
  margin-bottom: 30px;
}
.breadcrumb {
  font-size: 0.9rem;
  color: var(--color-text-tertiary, #94a3b8);
  display: flex;
  align-items: center;
  gap: 6px;
}
.breadcrumb .current {
  color: var(--color-primary, #2563eb);
  font-weight: 600;
}
.btn-add {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid var(--color-primary, #2563eb);
  color: var(--color-primary, #2563eb);
  background: transparent;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-add:hover {
  background: var(--color-primary, #2563eb);
  color: #fff;
}

/* ── 카드 공통 ── */
.card {
  background: var(--color-bg-card, #ffffff);
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
  padding: 24px;
}

/* ── 총 자산 (Hero) ── */
.net-worth-section {
  margin-bottom: 30px;
}
.section-label {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-secondary, #64748b);
  font-weight: 600;
}
.net-worth-value {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin: 8px 0;
}
.amount {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--color-primary, #0f172a);
  margin: 0;
  letter-spacing: -0.02em;
}
.badge-live {
  background: #dbeafe;
  color: #1d4ed8;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}
.update-time {
  font-size: 0.8rem;
  color: var(--color-text-tertiary, #94a3b8);
  display: flex;
  align-items: center;
  gap: 4px;
  margin: 0;
}

/* ── 그리드 레이아웃 ── */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 24px;
  margin-bottom: 40px;
}
@media (max-width: 768px) {
  .dashboard-grid { grid-template-columns: 1fr; }
}

/* ── 자산 비중 (왼쪽) ── */
.chart-card {
  display: flex;
  flex-direction: column;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.card-header h3 { margin: 0; font-size: 1.1rem; font-weight: 600; }
.card-header i { color: var(--color-text-tertiary, #94a3b8); font-size: 1.2rem; }

.allocation-bars {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: auto;
  margin-bottom: auto;
}
.alloc-item { display: flex; flex-direction: column; gap: 8px; }
.alloc-item.disabled { opacity: 0.4; }
.alloc-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
}
.alloc-info strong { font-weight: 600; }
.bar-bg {
  width: 100%;
  height: 8px;
  background: var(--color-bg-secondary, #f1f5f9);
  border-radius: 4px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  background: var(--color-primary, #2563eb);
  border-radius: 4px;
}

/* ── 자산 리스트 (오른쪽) ── */
.list-card { padding: 0; overflow: hidden; }
.list-header {
  display: flex;
  justify-content: space-between;
  padding: 16px 24px;
  background: var(--color-bg-page, #f8fafc);
  border-bottom: 1px solid var(--color-border, #e2e8f0);
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-text-secondary, #64748b);
}
.list-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  transition: background 0.2s;
  cursor: pointer;
}
.list-row:hover { background: var(--color-bg-page, #f8fafc); }
.list-row:hover .arrow { color: var(--color-primary, #2563eb); transform: translateX(4px); }

.asset-info { display: flex; align-items: center; gap: 16px; }
.icon-box {
  width: 48px;
  height: 48px;
  background: #eff6ff;
  color: #2563eb;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}
.asset-name { margin: 0 0 4px; font-weight: 600; font-size: 1rem; }
.asset-count { margin: 0; font-size: 0.8rem; color: var(--color-primary, #2563eb); font-weight: 500; }

.asset-value-wrap { display: flex; align-items: center; gap: 16px; }
.asset-value { font-size: 1.1rem; font-weight: 700; }
.arrow { color: var(--color-text-tertiary, #cbd5e1); transition: all 0.2s; }

/* ── 예적금 포트폴리오 (하단) ── */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 20px;
}
.section-header h3 { margin: 0; font-size: 1.2rem; font-weight: 700; }
.link-more {
  font-size: 0.85rem;
  color: var(--color-text-secondary, #64748b);
  text-decoration: none;
  transition: color 0.2s;
}
.link-more:hover { color: var(--color-primary, #2563eb); text-decoration: underline; }

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px 20px;
  color: var(--color-text-secondary, #64748b);
}
.empty-state i { font-size: 3rem; opacity: 0.5; }
.btn-primary {
  margin-top: 12px;
  background: var(--color-primary, #2563eb);
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
  transition: background 0.2s;
}
.btn-primary:hover { background: #1d4ed8; }

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}
.product-card {
  display: flex;
  flex-direction: column;
  transition: border-color 0.2s, box-shadow 0.2s;
  cursor: pointer;
}
.product-card:hover {
  border-color: var(--color-primary, #2563eb);
  box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
}
.product-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}
.icon-box-small {
  width: 36px;
  height: 36px;
  background: #f1f5f9;
  color: #64748b;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}
.bank-badge {
  background: #eff6ff;
  color: #1d4ed8;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}
.product-body { display: flex; flex-direction: column; gap: 8px; }
.product-name {
  margin: 0;
  font-size: 0.95rem;
  color: var(--color-text-secondary, #475569);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.product-amount { margin: 0; font-size: 1.4rem; font-weight: 700; color: #0f172a; }
.product-rate {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  color: #10b981;
  font-weight: 600;
  margin-top: 4px;
}

/* 로딩 스피너 */
.loading-state { display: flex; justify-content: center; padding: 100px 0; }
.spinner {
  width: 40px; height: 40px;
  border: 4px solid #e2e8f0;
  border-top-color: var(--color-primary, #2563eb);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }


/* ⭐ [신규 추가] 주식 섹션 전용 스타일 */
.stock-icon {
  background: #fef2f2;
  color: #ef4444;
}
.stock-icon-small {
  background: #fef2f2;
  color: #ef4444;
}
.stock-badge {
  background: #fef2f2;
  color: #ef4444;
}
.stock-detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: var(--color-text-secondary, #475569);
  margin-top: 4px;
}
.stock-detail-row strong {
  color: var(--color-text-primary, #0f172a);
  font-weight: 600;
}
/* 기존 .product-card 스타일을 찾아서 position: relative 추가 */
.product-card {
  position: relative;   /* ⭐ [수정] 삭제 버튼 absolute 배치를 위해 추가 */
  display: flex;
  flex-direction: column;
  transition: border-color 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

/* ⭐ [신규 추가] 카드 우측 상단 삭제 버튼 */
.btn-delete-asset {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 50%;
  background: #f1f5f9;
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 13px;
  line-height: 1;
  padding: 0;
  z-index: 2;
  transition: background 0.15s, color 0.15s;
}
.btn-delete-asset:hover {
  background: #fef2f2;
  color: #ef4444;
}

/* ⭐ [신규 추가] 보유수량 수정 UI 스타일 */
.qty-display {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
}
.qty-edit-icon {
  font-size: 13px;
  line-height: 1;
  color: #cbd5e1;
}
.qty-display:hover .qty-edit-icon { color: #2563eb; }

.qty-edit-group {
  display: flex;
  align-items: center;
  gap: 4px;
}
.qty-edit-input {
  width: 70px;
  padding: 3px 6px;
  border: 1px solid #2563eb;
  border-radius: 6px;
  font-size: 0.82rem;
}
.btn-qty-save, .btn-qty-cancel {
  width: 22px;
  height: 22px;
  border: none;
  border-radius: 50%;
  font-size: 11px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.btn-qty-save { background: #dbeafe; color: #2563eb; }
.btn-qty-cancel { background: #f1f5f9; color: #94a3b8; }
.btn-qty-save:hover { background: #2563eb; color: #fff; }
.btn-qty-cancel:hover { background: #ef4444; color: #fff; }

/* ⭐ [신규 추가] 현금 자산 추가 모달 스타일 */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-box {
  background: #fff;
  border-radius: 12px;
  padding: 28px;
  width: 340px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
}
.modal-box h3 { margin: 0 0 4px; font-size: 18px; }
.modal-symbol { color: #888; font-size: 13px; margin-bottom: 20px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 13px; color: #555; margin-bottom: 6px; }
.form-group input {
  width: 100%; padding: 10px 12px;
  border: 1px solid #ddd; border-radius: 8px;
  font-size: 15px; box-sizing: border-box;
}
.modal-actions { display: flex; gap: 10px; margin-top: 24px; }
.btn-cancel {
  flex: 1; padding: 10px; border: 1px solid #ddd;
  border-radius: 8px; background: #f5f5f5; cursor: pointer;
}
.btn-save {
  flex: 1; padding: 10px; border: none;
  border-radius: 8px; background: #2563eb; color: #fff;
  cursor: pointer; font-weight: 600;
}
.btn-save:disabled { background: #aaa; cursor: not-allowed; }

/* ⭐ [신규 추가] 현금 아이콘 색상 */
.cash-icon {
  background: #ecfdf5;
  color: #10b981;
}
/* ⭐ [신규 추가] 자산이 없을 때 표시 */
.empty-chart-text {
  color: var(--color-text-tertiary, #94a3b8);
  font-size: 0.9rem;
  text-align: center;
  padding: 40px 0;
}
/* ⭐ [신규 추가] 도넛차트를 카드 중앙에 배치 */
.donut-center-wrap {
  display: flex;
  justify-content: center;
  align-items: center;
  flex: 1;
  width: 100%;
  padding: 12px 0;
}
.donut-center-wrap :deep(.donut-wrap) {
  width: 100%;
  display: flex;
  justify-content: center;
}
.donut-center-wrap :deep(.donut-layout) {
  justify-content: center;
}
/* ⭐ [신규 추가] 예적금/주식 전체를 감싸는 바깥 큰 카드 */
.outer-section-card {
  background: var(--color-bg-card, #ffffff);
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 16px;
  padding: 28px;
  margin-bottom: 24px;
}

/* ⭐ [수정] 기존 .product-card(바깥 카드 스타일)를 안쪽 카드용(.product-card-inner)으로 대체 */
.product-card-inner {
  position: relative;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-page, #f8fafc);   /* 바깥 카드와 구분되도록 살짝 톤 다운된 배경 */
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 12px;
  padding: 20px;
  transition: border-color 0.2s, box-shadow 0.2s;
  cursor: pointer;
}
.product-card-inner:hover {
  border-color: var(--color-primary, #2563eb);
  box-shadow: 0 4px 10px -2px rgba(0,0,0,0.06);
}
.crypto-icon { background: #fffbeb; color: #f59e0b; }
.crypto-icon-small { background: #fffbeb; color: #f59e0b; }
.crypto-badge { background: #fffbeb; color: #d97706; }
</style>