<!-- src/views/OnboardingView.vue -->
<template>
  <div class="onboarding-container">
    <div class="onboarding-card">

      <div class="step-indicator">
        <span
          v-for="n in 4"
          :key="n"
          class="step-dot"
          :class="{ active: n === step, done: n < step }"
        />
      </div>

      <!-- STEP 1: 자산 규모 -->
      <div v-if="step === 1" class="step-content">
        <h2>현재 보유 자산 규모는 어느 정도인가요?</h2>
        <div class="option-grid">
          <button
            v-for="opt in ASSET_OPTIONS"
            :key="opt.value"
            class="option-btn"
            :class="{ selected: formData.asset_range === opt.value }"
            @click="formData.asset_range = opt.value"
          >
            {{ opt.label }}
          </button>
        </div>
      </div>

      <!-- STEP 2: 관심 자산 (다중 선택) -->
      <div v-else-if="step === 2" class="step-content">
        <h2>관심 있는 자산을 모두 선택해주세요</h2>
        <div class="option-grid">
          <button
            v-for="opt in INTEREST_OPTIONS"
            :key="opt.value"
            class="option-btn"
            :class="{ selected: formData.interest_assets.includes(opt.value) }"
            @click="toggleInterest(opt.value)"
          >
            {{ opt.label }}
          </button>
        </div>
      </div>

      <!-- STEP 3: 투자 성향 -->
      <div v-else-if="step === 3" class="step-content">
        <h2>투자 성향을 선택해주세요</h2>
        <div class="option-grid option-grid--col">
          <button
            v-for="opt in RISK_OPTIONS"
            :key="opt.value"
            class="option-btn"
            :class="{ selected: formData.risk_type === opt.value }"
            @click="formData.risk_type = opt.value"
          >
            {{ opt.label }}
          </button>
        </div>
      </div>

      <!-- STEP 4: 월 여유자금 -->
      <div v-else-if="step === 4" class="step-content">
        <h2>매달 투자/저축에 쓸 수 있는 여유자금은?</h2>
        <div class="option-grid">
          <button
            v-for="opt in BUDGET_OPTIONS"
            :key="opt.value"
            class="option-btn"
            :class="{ selected: formData.monthly_budget === opt.value }"
            @click="formData.monthly_budget = opt.value"
          >
            {{ opt.label }}
          </button>
        </div>
      </div>

      <div class="step-actions">
        <button v-if="step > 1" class="btn-prev" @click="goPrev">이전</button>
        <button
          v-if="step < 4"
          class="btn-next"
          :disabled="!canProceed"
          @click="goNext"
        >
          다음
        </button>
        <button
          v-else
          class="btn-submit"
          :disabled="!canProceed || isSubmitting"
          @click="submitOnboarding"
        >
          {{ isSubmitting ? '제출 중...' : '완료' }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from '@/api/axios'

const router = useRouter()
const route  = useRoute()

const step = ref(Number(route.query.step) || 1)
const isSubmitting = ref(false)

const formData = ref({
  asset_range: '',
  interest_assets: [],
  risk_type: '',
  monthly_budget: '',
})

const ASSET_OPTIONS = [
  { value: 'low',   label: '500만 미만' },
  { value: 'mid',   label: '500만 ~ 2,000만' },
  { value: 'high',  label: '2,000만 ~ 5,000만' },
  { value: 'vhigh', label: '5,000만 이상' },
]
const INTEREST_OPTIONS = [
  { value: 'deposit', label: '예/적금' },
  { value: 'stock',   label: '주식' },
  { value: 'crypto',  label: '코인' },
  { value: 'gold',    label: '금/은' },
]
const RISK_OPTIONS = [
  { value: 'safe',       label: '안정형 — 원금 보전이 가장 중요해요' },
  { value: 'neutral',    label: '중립형 — 적당한 위험을 감수할 수 있어요' },
  { value: 'aggressive', label: '공격형 — 고수익을 위해 위험을 감수해요' },
]
const BUDGET_OPTIONS = [
  { value: 'low',   label: '10만원 미만' },
  { value: 'mid',   label: '10만 ~ 50만원' },
  { value: 'high',  label: '50만 ~ 100만원' },
  { value: 'vhigh', label: '100만원 이상' },
]

watch(() => route.query.step, (newStep) => {
  step.value = Number(newStep) || 1
})

onMounted(() => {
  if (!route.query.step) {
    router.replace({ query: { step: 1 } })
  }
})

const canProceed = computed(() => {
  if (step.value === 1) return !!formData.value.asset_range
  if (step.value === 2) return formData.value.interest_assets.length > 0
  if (step.value === 3) return !!formData.value.risk_type
  if (step.value === 4) return !!formData.value.monthly_budget
  return false
})

function toggleInterest(value) {
  const list = formData.value.interest_assets
  const idx = list.indexOf(value)
  if (idx === -1) list.push(value)
  else list.splice(idx, 1)
}

function goNext() {
  if (!canProceed.value) return
  router.push({ query: { step: step.value + 1 } })
}
function goPrev() {
  router.push({ query: { step: step.value - 1 } })
}

const submitOnboarding = async () => {
  if (!canProceed.value) return alert('모든 항목을 선택해주세요.')

  isSubmitting.value = true
  try {
    await axios.post('/api/accounts/onboarding/', formData.value)

    localStorage.setItem('is_onboarded', 'true')

    alert('맞춤형 서비스 준비가 완료되었습니다! 대시보드로 이동합니다.')
    router.push('/')
  } catch (error) {
    console.error('온보딩 제출 실패:', error)
    if (error.response?.status === 401) {
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
  min-height: calc(100vh - 56px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  padding: 24px;
  font-family: 'Inter', sans-serif;
}
.onboarding-card {
  width: 100%;
  max-width: 520px;
  background: #ffffff;
  border: 1px solid #e1e3e4;
  padding: 40px;
}

.step-indicator { display: flex; gap: 8px; justify-content: center; margin-bottom: 32px; }
.step-dot { width: 8px; height: 8px; border-radius: 50%; background: #e1e3e4; }
.step-dot.active { background: #0050cc; width: 24px; border-radius: 4px; }
.step-dot.done { background: #191c1d; }

.step-content h2 {
  font-family: 'Hanken Grotesk', sans-serif;
  font-size: 1.25rem;
  font-weight: 700;
  color: #191c1d;
  margin: 0 0 24px;
  text-align: center;
  line-height: 1.4;
}

.option-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.option-grid--col { grid-template-columns: 1fr; }

.option-btn {
  padding: 14px 16px;
  border: 1px solid #cfc4c5;
  background: #ffffff;
  color: #191c1d;
  font-size: .88rem;
  font-weight: 500;
  cursor: pointer;
  text-align: left;
  transition: border-color .12s, background .12s;
}
.option-btn:hover { border-color: #191c1d; }
.option-btn.selected {
  border-color: #0050cc;
  background: #f0f6ff;
  color: #0050cc;
  font-weight: 700;
}

.step-actions {
  display: flex;
  gap: 10px;
  margin-top: 32px;
}
.btn-prev, .btn-next, .btn-submit {
  flex: 1;
  padding: 12px;
  border: 1px solid #191c1d;
  font-size: .9rem;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  transition: background .12s;
}
.btn-prev { background: #ffffff; color: #191c1d; }
.btn-prev:hover { background: #f1f5f9; }
.btn-next, .btn-submit { background: #191c1d; color: #ffffff; }
.btn-next:hover, .btn-submit:hover { background: #0050cc; border-color: #0050cc; }
.btn-next:disabled, .btn-submit:disabled { background: #cfc4c5; border-color: #cfc4c5; cursor: not-allowed; }
</style>