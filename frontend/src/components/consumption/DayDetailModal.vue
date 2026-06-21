<!-- src/components/consumption/DayDetailModal.vue -->
<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal">
      <div class="modal__header">
        <h3>{{ date }} 소비 내역</h3>
        <button @click="emit('close')">✕</button>
      </div>

      <p class="modal__total">총 {{ total.toLocaleString() }}원</p>

      <ul class="modal__list">
        <li v-for="tx in transactions" :key="tx.id" class="modal__item">
          <div class="modal__item-left">
            <span class="modal__time">{{ formatTime(tx.transacted_at) }}</span>
            <span class="modal__desc">{{ tx.description }}</span>
            <CategoryBadge :category="tx.category" :label="tx.category_display" />
            <span v-if="tx.is_settle_target" class="settle-tag" :class="{ done: tx.is_settled }">
              {{ tx.is_settled ? '✅ 정산완료' : '⏳ 정산대기' }}
            </span>
          </div>

          <div class="modal__item-right">
            <span class="modal__amount">{{ tx.amount.toLocaleString() }}원</span>

            <!-- 이체 건: 지출로 전환 -->
            <button
              v-if="tx.transaction_type === 'transfer'"
              class="btn-convert"
              @click="openConvert(tx)"
            >
              지출로 변경
            </button>

            <!-- 지출 건: 정산 대상 지정/해제 -->
            <button
              v-else-if="tx.transaction_type === 'expense'"
              class="btn-settle"
              :class="{ active: tx.is_settle_target }"
              @click="toggleSettle(tx)"
            >
              {{ tx.is_settle_target ? 'N빵 해제' : 'N빵 정산' }}
            </button>
          </div>
        </li>
      </ul>

      <!-- 카테고리 전환 패널 -->
      <div v-if="convertTarget" class="convert-panel">
        <p>카테고리 선택</p>
        <select v-model="newCategory">
          <option v-for="c in CATEGORIES" :key="c.value" :value="c.value">{{ c.label }}</option>
        </select>
        <button @click="confirmConvert">확인</button>
        <button @click="convertTarget = null">취소</button>
      </div>

      <!-- 정산 계산 패널 -->
      <div v-if="settleTarget" class="settle-panel">
        <p>총 <strong>{{ settleTarget.amount.toLocaleString() }}원</strong>을 몇 명이 나눠 냈나요? (본인 포함)</p>
        <input type="number" v-model.number="peopleCount" min="2" placeholder="인원수" />

        <div v-if="peopleCount >= 2" class="settle-preview">
          인당 <strong>{{ Math.floor(settleTarget.amount / peopleCount).toLocaleString() }}원</strong>
          → 받을 돈 <strong style="color:#3b6fd4">
            {{ (Math.floor(settleTarget.amount / peopleCount) * (peopleCount - 1)).toLocaleString() }}원
          </strong>
        </div>

        <div class="settle-panel__actions">
          <button @click="confirmSettleCalculate" :disabled="!peopleCount || peopleCount < 2">계산 완료</button>
          <button @click="settleTarget = null">취소</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDayDetail, updateCategory, toggleSettleTarget, calculateSettle } from '@/api/consumption'
import CategoryBadge from './CategoryBadge.vue'

const props = defineProps({ date: String })
const emit  = defineEmits(['close'])

const transactions = ref([])
const total         = ref(0)

const convertTarget = ref(null)
const newCategory    = ref('food')

const settleTarget  = ref(null)
const peopleCount   = ref(null)

const CATEGORIES = [
  { value:'food', label:'식비' }, { value:'cafe', label:'카페' },
  { value:'transport', label:'교통' }, { value:'shopping', label:'쇼핑' },
  { value:'convenience', label:'편의점' }, { value:'health', label:'의료/건강' },
  { value:'culture', label:'문화/여가' }, { value:'etc', label:'기타' },
]

onMounted(async () => {
  const { data } = await getDayDetail(props.date)
  transactions.value = data.transactions
  total.value        = data.total
})

const formatTime = (iso) =>
  new Date(iso).toLocaleTimeString('ko-KR', { hour:'2-digit', minute:'2-digit' })

// 카테고리 전환
const openConvert = (tx) => { convertTarget.value = tx; newCategory.value = 'food' }
const confirmConvert = async () => {
  await updateCategory(convertTarget.value.id, newCategory.value)
  const tx = transactions.value.find(t => t.id === convertTarget.value.id)
  if (tx) {
    tx.transaction_type = 'expense'
    tx.category          = newCategory.value
    tx.category_display  = CATEGORIES.find(c => c.value === newCategory.value)?.label
    total.value += tx.amount
  }
  convertTarget.value = null
}

// 정산 대상 토글
const toggleSettle = async (tx) => {
  const { data } = await toggleSettleTarget(tx.id)
  Object.assign(tx, data)
  // 방금 정산 대상으로 켰으면 바로 인원수 입력 패널 오픈
  if (tx.is_settle_target) {
    settleTarget.value = tx
    peopleCount.value  = null
  }
}

// 정산 금액 계산 확정
const confirmSettleCalculate = async () => {
  const { data } = await calculateSettle(settleTarget.value.id, peopleCount.value)
  const tx = transactions.value.find(t => t.id === settleTarget.value.id)
  if (tx) Object.assign(tx, data)
  settleTarget.value = null
}
</script>

<style scoped>
.modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,.4); display:flex; align-items:center; justify-content:center; z-index:100; }
.modal { background:#fff; border-radius:16px; width:480px; max-height:80vh; overflow-y:auto; padding:1.5rem; }
.modal__header { display:flex; justify-content:space-between; align-items:center; margin-bottom:.5rem; }
.modal__total  { color:#6c63ff; font-weight:700; font-size:1.1rem; margin-bottom:1rem; }
.modal__list   { list-style:none; padding:0; margin:0; }
.modal__item   { display:flex; justify-content:space-between; align-items:center; padding:.7rem 0; border-bottom:1px solid #f0f0f0; gap: .5rem; }
.modal__item-left { display:flex; flex-direction:column; gap:4px; flex: 1; }
.modal__time   { font-size:.75rem; color:#aaa; }
.modal__desc   { font-size:.95rem; font-weight:500; }
.modal__item-right { display:flex; flex-direction:column; align-items:flex-end; gap:.4rem; }
.modal__amount { font-weight:700; }

.btn-convert, .btn-settle {
  font-size:.75rem; border:none; border-radius:6px; padding:3px 8px; cursor:pointer;
}
.btn-convert { background:#f0f4ff; color:#6c63ff; }
.btn-settle  { background:#f1f5f9; color:#64748b; }
.btn-settle.active { background:#fff7ed; color:#f59e0b; }

.settle-tag {
  font-size:.7rem; font-weight:600; color:#f59e0b; width:fit-content;
}
.settle-tag.done { color:#16a34a; }

.convert-panel, .settle-panel {
  margin-top:1rem; padding:1rem; background:#f9f9f9; border-radius:8px;
}
.convert-panel { display:flex; gap:.5rem; align-items:center; }
.settle-panel p { font-size:.85rem; margin: 0 0 .6rem; }
.settle-panel input {
  width:100%; padding:.5rem; border:1px solid #ddd; border-radius:6px; margin-bottom:.6rem;
}
.settle-preview { font-size:.85rem; color:#444; margin-bottom:.8rem; background:#fff; padding:.6rem; border-radius:6px; }
.settle-panel__actions { display:flex; gap:.5rem; }
.settle-panel__actions button {
  flex:1; padding:.5rem; border-radius:6px; border:none; cursor:pointer; font-weight:600;
}
.settle-panel__actions button:first-child { background:#3b6fd4; color:#fff; }
.settle-panel__actions button:first-child:disabled { background:#cbd5e1; cursor:not-allowed; }
.settle-panel__actions button:last-child { background:#f1f5f9; color:#64748b; }
</style>