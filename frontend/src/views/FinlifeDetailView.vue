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

        <!-- 가입 액션 섹션 -->
        <div class="action-section">
          <div class="join-links">

            <button
              class="btn btn-primary btn-large"
              @click="goToPortfolio"
            >
              <i class="ti ti-external-link" aria-hidden="true"></i>
              금융상품 가입하기
            </button>

            <a
              v-if="product.can_join_online && product.bank_home_url"
              :href="resolvedBankUrl"
              target="_blank"
              rel="noopener noreferrer"
              class="btn btn-outline btn-large"
            >
              <i class="ti ti-building-bank" aria-hidden="true"></i>
              {{ product.kor_co_nm }} 공식 홈페이지
            </a>

            <!-- 온라인 가입 불가 안내 -->
            <div v-else-if="!product.can_join_online" class="offline-notice">
              <i class="ti ti-info-circle"></i>
              이 상품은 영업점 방문을 통해서만 가입할 수 있습니다.
            </div>

          </div>

          <!-- 비로그인이어도 외부 링크는 허용, 안내만 표시 -->
          <p v-if="!authStore.isLoggedIn" class="login-hint">
            <router-link to="/login">로그인</router-link> 후 관심상품으로 저장할 수 있습니다.
          </p>
          <button
            v-else
            class="btn-wishlist"
            :class="{ active: isWishlisted }"
            @click="toggleWishlist"
          >
            <i :class="isWishlisted ? 'ti ti-heart-filled' : 'ti ti-heart'"></i>
            {{ isWishlisted ? '관심상품 저장됨' : '관심상품 저장' }}
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { finlifeAPI } from '@/api/finlife'
import { DEMO_PRODUCT_URL_MAP } from '@/constants/demoProductLinks'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const product = ref(null)
const isLoading = ref(true)
const isWishlisted = ref(false)

const productId = route.params.id

const resolvedBankUrl = computed(() => {
  if (!product.value) return null
  const demoUrl = DEMO_PRODUCT_URL_MAP[product.value.fin_prdt_cd]
  return demoUrl || product.value.bank_home_url
})

async function goToPortfolio() {
  try {
    const { data } = await finlifeAPI.joinProduct(productId)
    alert(data.message || '가입이 완료되었습니다!')
    router.push({ name: 'mypage' })
  } catch (error) {
    if (error.response?.status === 401) {
      alert('로그인이 필요한 기능입니다.')
      router.push({ name: 'login', query: { redirect: route.fullPath } })
    } else if (error.response?.status === 400) {
      // 이미 가입된 상품인 경우 등
      alert(error.response.data?.error || '이미 가입된 상품입니다.')
      router.push({ name: 'mypage' })
    } else {
      console.error('가입 처리 실패:', error)
      alert('가입 처리 중 오류가 발생했습니다.')
    }
  }
}

async function fetchProductDetail() {
  try {
    const { data } = await finlifeAPI.getProductDetail(productId)
    product.value = data
    // 위시리스트 여부 체크 (API에 필드 있으면)
    isWishlisted.value = data.is_wishlisted ?? false
  } catch (error) {
    console.error('상세 정보 로드 실패:', error)
    alert('상품 정보를 불러오지 못했습니다.')
    router.push('/finlife')
  } finally {
    isLoading.value = false
  }
}

async function toggleWishlist() {
  try {
    if (isWishlisted.value) {
      await finlifeAPI.removeWishlist(productId)
      isWishlisted.value = false
    } else {
      await finlifeAPI.addWishlist(productId)
      isWishlisted.value = true
    }
  } catch (error) {
    alert('처리 중 오류가 발생했습니다.')
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

/* 액션 섹션 */
.action-section { text-align: center; padding-top: 16px; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.join-links { display: flex; flex-direction: column; align-items: center; gap: 12px; width: 100%; }
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 12px 24px; border-radius: var(--radius-md); font-size: 0.95rem; font-weight: 600; font-family: var(--font-main); text-decoration: none; cursor: pointer; border: none; transition: all 0.15s; }
.btn-primary { background: var(--color-primary); color: white; }
.btn-primary:hover { background: var(--color-primary-hover); }
.btn-large { width: 100%; max-width: 360px; padding: 16px; font-size: 1.05rem; }
.btn-outline { background: var(--color-bg-card); color: var(--color-text-primary); border: 0.5px solid var(--color-border-strong); }
.btn-outline:hover { background: var(--color-bg-secondary); }

.offline-notice { display: flex; align-items: center; gap: 8px; font-size: 0.85rem; color: var(--color-text-secondary); background: var(--color-bg-secondary); border-radius: var(--radius-md); padding: 12px 20px; }
.offline-notice i { font-size: 18px; flex-shrink: 0; }

.login-hint { font-size: 0.85rem; color: var(--color-text-tertiary); margin: 0; }
.login-hint a { color: var(--color-primary); text-decoration: none; font-weight: 600; }

.btn-wishlist { display: inline-flex; align-items: center; gap: 6px; background: transparent; border: 0.5px solid var(--color-border-strong); border-radius: var(--radius-md); padding: 8px 20px; font-size: 0.85rem; font-weight: 500; font-family: var(--font-main); color: var(--color-text-secondary); cursor: pointer; transition: all 0.15s; }
.btn-wishlist:hover { border-color: var(--color-primary); color: var(--color-primary); }
.btn-wishlist.active { background: color-mix(in srgb, var(--color-primary) 8%, transparent); border-color: var(--color-primary); color: var(--color-primary); }
.btn-wishlist i { font-size: 16px; }

.skeleton-container { background: var(--color-bg-card); border-radius: var(--radius-lg); padding: 3rem; }
.skeleton { background: linear-gradient(90deg, #eee 25%, #e0e0e0 50%, #eee 75%); background-size: 200% 100%; animation: shimmer 1.4s infinite; border-radius: var(--radius-md); }
.skeleton-title { height: 140px; margin-bottom: 40px; }
.skeleton-body { height: 400px; }
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
</style>