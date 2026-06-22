// frontend/src/views/FinlifeDetailView.vue
<template>
  <div class="detail-page">
    <div class="section-inner max-w-800">
      
      <button class="btn-back" @click="router.push('/finlife')">
        <i class="ti ti-arrow-left" aria-hidden="true"></i> 목록으로
      </button>

      <div v-if="isLoading" class="skeleton-container">
        <div class="skeleton skeleton-title"></div>
        <div class="skeleton skeleton-body"></div>
      </div>

      <div v-else-if="product" class="detail-card">
        <div class="detail-header">
          <p class="bank-name">{{ product.kor_co_nm }}</p>
          <h1 class="product-name">{{ product.fin_prdt_nm }}</h1>
          <p class="product-desc">{{ product.etc_note || '상세 설명이 제공되지 않은 상품입니다.' }}</p>
        </div>

        <div class="detail-section">
          <h2 class="section-title">기간별 금리 안내</h2>
          <div class="options-grid">
            <div v-for="option in product.options" :key="option.save_trm" class="option-card">
              <div class="term-badge">{{ option.save_trm }}개월</div>
              <div class="rate-row">
                <span class="rate-title">기본 금리</span>
                <span class="rate-num">{{ option.intr_rate }}%</span>
              </div>
              <div class="rate-row highlight">
                <span class="rate-title">최고 우대금리</span>
                <span class="rate-num">{{ option.intr_rate2 }}%</span>
              </div>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h2 class="section-title">가입 정보</h2>
          <div class="info-box">
            <div class="info-row">
              <i class="ti ti-users text-muted"></i>
              <div class="info-text">
                <strong>가입 대상</strong>
                <p>{{ product.join_member || '제한 없음' }}</p>
              </div>
            </div>
            <div class="info-row">
              <i class="ti ti-device-mobile text-muted"></i>
              <div class="info-text">
                <strong>가입 방법</strong>
                <p>{{ product.join_way || '영업점, 인터넷, 스마트폰' }}</p>
              </div>
            </div>
            <div class="info-row">
              <i class="ti ti-star text-muted"></i>
              <div class="info-text">
                <strong>우대 조건</strong>
                <p>{{ product.spcl_cnd || '해당 없음' }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="action-section">
          <template v-if="authStore.isLoggedIn">
            <button 
              class="btn btn-primary btn-large" 
              @click="handleJoin"
              :disabled="isJoining"
            >
              <i class="ti ti-check" aria-hidden="true"></i>
              {{ isJoining ? '가입 처리 중...' : '상품 가입하기' }}
            </button>
          </template>
          <template v-else>
            <div class="login-prompt">
              <p>상품에 가입하려면 로그인이 필요합니다.</p>
              <router-link to="/login" class="btn btn-outline">로그인</router-link>
            </div>
          </template>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { finlifeAPI } from '@/api/finlife'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const product = ref(null)
const isLoading = ref(true)
const isJoining = ref(false)

const productId = route.params.id

async function fetchProductDetail() {
  try {
    const { data } = await finlifeAPI.getProductDetail(productId)
    product.value = data
  } catch (error) {
    console.error('상세 정보 로드 실패:', error)
    alert('상품 정보를 불러오지 못했습니다.')
    router.push('/finlife')
  } finally {
    isLoading.value = false
  }
}

async function handleJoin() {
  if (!confirm(`[${product.value.fin_prdt_nm}] 상품에 가입하시겠습니까?`)) return

  isJoining.value = true
  try {
    await finlifeAPI.joinProduct(productId)
    alert('가입이 완료되었습니다. 마이페이지에서 확인하세요.')
    router.push('/mypage')
  } catch (error) {
    if (error.response?.data?.error === '이미 가입된 상품입니다.') {
      alert('이미 가입된 상품입니다.')
    } else {
      alert('가입 처리 중 오류가 발생했습니다.')
    }
  } finally {
    isJoining.value = false
  }
}

onMounted(() => {
  fetchProductDetail()
})
</script>

<style scoped>
.detail-page { min-height: 100vh; background: var(--color-bg-page); font-family: var(--font-main); color: var(--color-text-primary); padding: 40px 0 80px; }
.section-inner.max-w-800 { max-width: 800px; margin: 0 auto; padding: 0 24px; }
.btn-back { background: transparent; border: none; color: var(--color-text-secondary); font-size: 0.9rem; font-weight: 500; font-family: var(--font-main); cursor: pointer; display: inline-flex; align-items: center; gap: 6px; margin-bottom: 24px; padding: 0; transition: color 0.15s; }
.btn-back i { font-size: 16px; }
.btn-back:hover { color: var(--color-primary); }

.detail-card { background: var(--color-bg-card); border: 0.5px solid var(--color-border); border-radius: var(--radius-lg); padding: 3rem 2.5rem; }
.detail-header { text-align: center; margin-bottom: 40px; padding-bottom: 32px; border-bottom: 0.5px solid var(--color-border); }
.bank-name { font-size: 14px; font-weight: 600; letter-spacing: 0.05em; color: var(--color-primary); margin: 0 0 12px; }
.product-name { font-size: 2.2rem; font-weight: 700; line-height: 1.35; margin: 0 0 16px; letter-spacing: -0.02em; }
.product-desc { font-size: 0.95rem; color: var(--color-text-secondary); line-height: 1.6; white-space: pre-wrap; margin: 0 auto; max-width: 600px; }

.detail-section { margin-bottom: 40px; }
.section-title { font-size: 1.1rem; font-weight: 600; margin: 0 0 16px; }

.options-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }
.option-card { background: var(--color-bg-secondary); border-radius: var(--radius-md); padding: 20px; }
.term-badge { display: inline-block; background: var(--color-bg-card); border: 0.5px solid var(--color-border-strong); color: var(--color-text-primary); padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; margin-bottom: 16px; }
.rate-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.rate-row:last-child { margin-bottom: 0; }
.rate-title { font-size: 0.85rem; color: var(--color-text-secondary); }
.rate-num { font-size: 1.05rem; font-weight: 600; }
.rate-row.highlight .rate-title, .rate-row.highlight .rate-num { color: var(--color-primary); font-weight: 700; }

.info-box { background: var(--color-bg-secondary); border-radius: var(--radius-md); padding: 24px; }
.info-row { display: flex; align-items: flex-start; gap: 16px; margin-bottom: 20px; }
.info-row:last-child { margin-bottom: 0; }
.info-row i { font-size: 24px; color: var(--color-text-tertiary); margin-top: 2px; }
.info-text strong { display: block; font-size: 0.9rem; color: var(--color-text-primary); margin-bottom: 4px; }
.info-text p { font-size: 0.9rem; color: var(--color-text-secondary); line-height: 1.5; margin: 0; }

.action-section { text-align: center; padding-top: 16px; }
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 12px 24px; border-radius: var(--radius-md); font-size: 0.95rem; font-weight: 600; font-family: var(--font-main); text-decoration: none; cursor: pointer; border: none; transition: all 0.15s; }
.btn-primary { background: var(--color-primary); color: white; }
.btn-primary:hover:not(:disabled) { background: var(--color-primary-hover); }
.btn-primary:disabled { background: var(--color-text-tertiary); cursor: not-allowed; }
.btn-large { width: 100%; max-width: 320px; padding: 16px; font-size: 1.05rem; }
.btn-outline { background: var(--color-bg-card); color: var(--color-text-primary); border: 0.5px solid var(--color-border-strong); }
.btn-outline:hover { background: var(--color-bg-secondary); }

.login-prompt { background: var(--color-bg-secondary); padding: 24px; border-radius: var(--radius-md); border: 0.5px dashed var(--color-border-strong); }
.login-prompt p { margin: 0 0 16px; color: var(--color-text-secondary); font-size: 0.95rem; }

.skeleton-container { background: var(--color-bg-card); border-radius: var(--radius-lg); padding: 3rem; }
.skeleton { background: linear-gradient(90deg, #eee 25%, #e0e0e0 50%, #eee 75%); background-size: 200% 100%; animation: shimmer 1.4s infinite; border-radius: var(--radius-md); }
.skeleton-title { height: 140px; margin-bottom: 40px; }
.skeleton-body { height: 400px; }
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
</style>