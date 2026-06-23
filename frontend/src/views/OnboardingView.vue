<template>
  <div class="onboarding-container">
    <h2>금융 여정 시작하기</h2>
    <button @click="submitOnboarding" :disabled="isSubmitting">완료</button>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from '@/api/axios' // 공통 axios 사용

const router = useRouter()
const route = useRoute()

const step = ref(Number(route.query.step) || 1)
const isSubmitting = ref(false)

const formData = ref({
  age: '',
  asset_range: '',
  interest_assets: [],
  risk_type: '',
  monthly_budget: ''
})

watch(() => route.query.step, (newStep) => {
  step.value = Number(newStep) || 1
})

onMounted(() => {
  if (!route.query.step) {
    router.replace({ query: { step: 1 } })
  }
})

const submitOnboarding = async () => {
  // 간단한 유효성 검사
  if (!formData.value.monthly_budget) return alert('월 여유자금을 선택해주세요.')

  isSubmitting.value = true

  try {
    // 백엔드 API 호출 (공통 axios 인터셉터가 토큰을 자동으로 헤더에 넣어줍니다)
    await axios.post('/api/accounts/onboarding/', formData.value)
    
    // 성공 시 로컬 스토리지 업데이트
    localStorage.setItem('is_onboarded', 'true')
    
    alert('맞춤형 서비스 준비가 완료되었습니다! 대시보드로 이동합니다.')
    router.push('/') 
    
  } catch (error) {
    console.error('온보딩 제출 실패:', error)
    if (error.response && error.response.status === 401) {
      alert('세션이 만료되었습니다. 다시 로그인해주세요.')
      router.push('/login')
    } else {
      alert('제출 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.')
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.onboarding-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}
</style>