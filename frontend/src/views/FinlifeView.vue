// frontend/src/views/FinlifeView.vue
<template>
  <div class="finlife-page">
    <div class="section-inner">
      <header class="page-header">
        <p class="eyebrow">FINANCIAL PRODUCTS</p>
        <h1 class="page-title">예적금 상품 찾기</h1>
        <p class="page-desc">
          금융감독원 데이터를 기반으로 최고 금리 상품을 한눈에 비교하세요.
        </p>
      </header>

      <section class="filter-section">
        <div class="filter-group">
          <button 
            class="filter-btn" 
            :class="{ active: selectedBank === '전체' }"
            @click="selectedBank = '전체'"
          >
            전체
          </button>
          <button 
            v-for="bank in banks" 
            :key="bank"
            class="filter-btn"
            :class="{ active: selectedBank === bank }"
            @click="selectedBank = bank"
          >
            {{ bank }}
          </button>
        </div>
      </section>

      <section class="product-section">
        <div class="section-header">
          <h2 class="section-title">상품 목록</h2>
          <span class="product-count">총 <strong>{{ filteredProducts.length }}</strong>개</span>
        </div>

        <div v-if="isLoading" class="product-grid">
          <div v-for="n in 6" :key="n" class="product-card skeleton"></div>
        </div>

        <div v-else-if="filteredProducts.length === 0" class="empty-state">
          <i class="ti ti-database-off" aria-hidden="true"></i>
          <p>해당 은행의 상품이 존재하지 않습니다.</p>
        </div>

        <div v-else class="product-grid">
          <router-link 
            v-for="product in filteredProducts" 
            :key="product.fin_prdt_cd"
            :to="`/finlife/${product.fin_prdt_cd}`"
            class="product-card"
          >
            <div class="card-top">
              <span class="bank-badge">{{ product.kor_co_nm }}</span>
              <h3 class="product-name">{{ product.fin_prdt_nm }}</h3>
            </div>
            
            <div class="card-bottom">
              <div class="rate-box">
                <p class="rate-label">기본 금리</p>
                <p class="rate-value">{{ getBaseRate(product.options) }}%</p>
              </div>
              <div class="rate-box highlight">
                <p class="rate-label">최고 우대금리</p>
                <p class="rate-value">{{ getMaxRate(product.options) }}%</p>
              </div>
            </div>
          </router-link>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { finlifeAPI } from '@/api/finlife' 

const products = ref([])
const isLoading = ref(true)
const selectedBank = ref('전체')

const banks = computed(() => {
  const bankSet = new Set(products.value.map(p => p.kor_co_nm))
  return Array.from(bankSet).sort()
})

const filteredProducts = computed(() => {
  if (selectedBank.value === '전체') return products.value
  return products.value.filter(p => p.kor_co_nm === selectedBank.value)
})

const getMaxRate = (options) => {
  if (!options || options.length === 0) return '-'
  const max = Math.max(...options.map(o => o.intr_rate2 || 0))
  return max > 0 ? max.toFixed(2) : '-'
}

const getBaseRate = (options) => {
  if (!options || options.length === 0) return '-'
  const max = Math.max(...options.map(o => o.intr_rate || 0))
  return max > 0 ? max.toFixed(2) : '-'
}

async function fetchProducts() {
  try {
    const { data } = await finlifeAPI.getProducts() 
    products.value = data
  } catch (error) {
    console.error('예적금 데이터를 불러오는 데 실패했습니다.', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.finlife-page {
  min-height: 100vh;
  background: var(--color-bg-page);
  font-family: var(--font-main);
  color: var(--color-text-primary);
  padding: 40px 0 80px;
}

.section-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px;
}

.page-header { margin-bottom: 32px; }
.eyebrow { font-size: 12px; font-weight: 600; letter-spacing: 0.1em; color: var(--color-primary); margin: 0 0 10px; }
.page-title { font-size: 2rem; font-weight: 700; line-height: 1.35; margin: 0 0 12px; letter-spacing: -0.02em; }
.page-desc { font-size: 0.95rem; color: var(--color-text-secondary); line-height: 1.6; margin: 0; }

.filter-section { margin-bottom: 32px; }
.filter-group { display: flex; flex-wrap: wrap; gap: 10px; }
.filter-btn { background: var(--color-bg-card); border: 0.5px solid var(--color-border-strong); color: var(--color-text-secondary); padding: 8px 18px; border-radius: 24px; font-size: 0.85rem; font-weight: 500; font-family: var(--font-main); cursor: pointer; transition: all 0.15s; }
.filter-btn:hover { background: var(--color-bg-secondary); }
.filter-btn.active { background: var(--color-primary); color: white; border-color: var(--color-primary); font-weight: 600; }

.section-header { display: flex; align-items: center; gap: 12px; margin-bottom: 18px; }
.section-title { font-size: 1.1rem; font-weight: 600; margin: 0; }
.product-count { font-size: 0.85rem; color: var(--color-text-secondary); }
.product-count strong { color: var(--color-primary); }

.product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }

.product-card { background: var(--color-bg-card); border: 0.5px solid var(--color-border); border-radius: var(--radius-lg); padding: 1.8rem; text-decoration: none; color: inherit; display: flex; flex-direction: column; justify-content: space-between; transition: transform 0.15s, border-color 0.15s; }
.product-card:hover { transform: translateY(-4px); border-color: var(--color-primary); }

.card-top { margin-bottom: 24px; }
.bank-badge { display: inline-block; font-size: 0.75rem; font-weight: 600; color: var(--color-text-tertiary); background: var(--color-bg-secondary); padding: 4px 10px; border-radius: var(--radius-md); margin-bottom: 12px; }
.product-name { font-size: 1.15rem; font-weight: 600; margin: 0; line-height: 1.4; word-break: keep-all; }

.card-bottom { display: flex; gap: 12px; }
.rate-box { flex: 1; background: var(--color-bg-secondary); border-radius: var(--radius-md); padding: 12px; text-align: center; }
.rate-box.highlight { background: var(--color-primary-light); }
.rate-label { font-size: 0.75rem; color: var(--color-text-secondary); margin: 0 0 4px; }
.rate-box.highlight .rate-label { color: var(--color-primary); }
.rate-value { font-size: 1.2rem; font-weight: 700; margin: 0; letter-spacing: -0.02em; }
.rate-box.highlight .rate-value { color: var(--color-primary); }

.empty-state { text-align: center; padding: 60px 0; color: var(--color-text-tertiary); background: var(--color-bg-card); border: 0.5px dashed var(--color-border-strong); border-radius: var(--radius-lg); }
.empty-state i { font-size: 32px; margin-bottom: 12px; display: block; }

.skeleton { height: 200px; background: linear-gradient(90deg, #eee 25%, #e0e0e0 50%, #eee 75%); background-size: 200% 100%; animation: shimmer 1.4s infinite; border: none; }
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

@media (max-width: 768px) { .product-grid { grid-template-columns: 1fr; } }
</style>