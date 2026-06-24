<template>
  <div class="portfolio-tab">
    
    <header class="port-header">
      <div class="breadcrumb">
        <span>Overview</span>
        <i class="ti ti-chevron-right"></i>
        <span class="current">Portfolio</span>
      </div>
      <button class="btn-add"><i class="ti ti-plus"></i> 자산 추가하기</button>
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
          
          <div class="allocation-bars">
            <div class="alloc-item">
              <div class="alloc-info">
                <span>예적금 (안전자산)</span>
                <strong>100%</strong>
              </div>
              <div class="bar-bg"><div class="bar-fill" style="width: 100%;"></div></div>
            </div>
            
            <div class="alloc-item disabled">
              <div class="alloc-info">
                <span>주식 및 크립토 (준비중)</span>
                <span>0%</span>
              </div>
              <div class="bar-bg"></div>
            </div>
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
          </div>
        </div>
      </section>

      <section class="portfolio-items">
        <div class="section-header">
          <h3>나의 예적금 포트폴리오</h3>
          <router-link to="/finlife" class="link-more">더 둘러보기</router-link>
        </div>

        <div v-if="assets.savings.length === 0" class="empty-state card">
          <i class="ti ti-pig-money"></i>
          <p>아직 가입한 예적금 상품이 없습니다.</p>
          <router-link to="/finlife" class="btn-primary">상품 찾아보기</router-link>
        </div>

        <div v-else class="product-grid">
          <div 
            v-for="product in assets.savings" 
            :key="product.id"
            class="product-card card"
          >
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

    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from '@/api/axios'

const isLoading = ref(true)

const summary = ref({ total_assets: 0 })
const assets = ref({
  savings: [],
  stocks: [],
  crypto: []
})

const totalSavings = computed(() => {
  return assets.value.savings.reduce((acc, curr) => acc + Number(curr.invested_amount), 0)
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
</style>