<!-- src/components/consumption/DayDetailModal.vue -->
<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal">
      <div class="modal__header">
        <h3>{{ date }}</h3>
        <button class="modal__close" @click="emit('close')">✕</button>
      </div>

      <p class="modal__total">{{ total.toLocaleString() }}원</p>

      <ul class="modal__list">
        <li v-for="tx in transactions" :key="tx.id" class="modal__item">
          <div class="modal__item-left">
            <span class="modal__time">{{ formatTime(tx.transacted_at) }}</span>
            <span class="modal__desc">{{ tx.description }}</span>
            <span class="modal__badge">{{ tx.category_display }}</span>
            <span v-if="tx.is_settle_target" class="settle-tag" :class="{ done: tx.is_settled }">
              {{ tx.is_settled ? '정산완료' : '정산대기' }}
            </span>
          </div>

          <div class="modal__item-right">
            <span class="modal__amount">{{ tx.amount.toLocaleString() }}원</span>

            <button
              v-if="tx.transaction_type === 'transfer'"
              class="btn-convert"
              @click="openConvert(tx)"
            >
              지출로 변경
            </button>

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

      <div v-if="convertTarget" class="convert-panel">
        <p>카테고리 선택</p>
        <select v-model="newCategory">
          <option v-for="c in CATEGORIES" :key="c.value" :value="c.value">{{ c.label }}</option>
        </select>
        <button class="panel-btn" @click="confirmConvert">확인</button>
        <button class="panel-btn panel-btn--ghost" @click="convertTarget = null">취소</button>
      </div>

      <div v-if="settleTarget" class="settle-panel">
        <p>총 <strong>{{ settleTarget.amount.toLocaleString() }}원</strong>을 몇 명이 나눠 냈나요? (본인 포함)</p>
        <input type="number" v-model.number="peopleCount" min="2" placeholder="인원수" />

        <div v-if="peopleCount >= 2" class="settle-preview">
          인당 <strong>{{ Math.floor(settleTarget.amount / peopleCount).toLocaleString() }}원</strong>
          → 받을 돈 <strong class="highlight">
            {{ (Math.floor(settleTarget.amount / peopleCount) * (peopleCount - 1)).toLocaleString() }}원
          </strong>
        </div>

        <div class="settle-panel__actions">
          <button class="panel-btn" @click="confirmSettleCalculate" :disabled="!peopleCount || peopleCount < 2">계산 완료</button>
          <button class="panel-btn panel-btn--ghost" @click="settleTarget = null">취소</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDayDetail, updateCategory, toggleSettleTarget, calculateSettle } from '@/api/consumption'

const props = defineProps({ date: String })
const emit  = defineEmits(['close', 'settle-changed'])

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
  emit('settle-changed')
}

const toggleSettle = async (tx) => {
  const { data } = await toggleSettleTarget(tx.id)
  Object.assign(tx, data)
  if (tx.is_settle_target) {
    settleTarget.value = tx
    peopleCount.value  = null
  }
}

const confirmSettleCalculate = async () => {
  const { data } = await calculateSettle(settleTarget.value.id, peopleCount.value)
  const tx = transactions.value.find(t => t.id === settleTarget.value.id)
  if (tx) Object.assign(tx, data)
  settleTarget.value = null
  emit('settle-changed')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0; background: rgba(25,28,29,.5);
  display: flex; align-items: center; justify-content: center; z-index: 100;
}
.modal {
  background: #fff; border: 1px solid #191c1d; width: 480px; max-height: 80vh;
  overflow-y: auto; padding: 24px; font-family: 'Inter', sans-serif;
}
.modal__header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.modal__header h3 { font-family: 'Hanken Grotesk', sans-serif; font-size: 1.1rem; font-weight: 700; color: #191c1d; }
.modal__close { background: none; border: none; font-size: 1rem; cursor: pointer; color: #4c4546; }
.modal__total { font-family: 'Hanken Grotesk', sans-serif; color: #0050cc; font-weight: 700; font-size: 1.2rem; margin-bottom: 16px; }
.modal__list   { list-style: none; padding: 0; margin: 0; }
.modal__item   { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #e1e3e4; gap: .5rem; }
.modal__item-left { display: flex; flex-direction: column; gap: 4px; flex: 1; }
.modal__time   { font-family: 'Geist', sans-serif; font-size: .7rem; color: #9a9192; }
.modal__desc   { font-size: .92rem; font-weight: 500; color: #191c1d; }
.modal__badge  {
  font-family: 'Geist', sans-serif; font-size: 10px; letter-spacing: .04em;
  border: 1px solid #cfc4c5; color: #4c4546; padding: 1px 6px; width: fit-content;
}
.modal__item-right { display: flex; flex-direction: column; align-items: flex-end; gap: .4rem; }
.modal__amount { font-family: 'Hanken Grotesk', sans-serif; font-weight: 700; color: #191c1d; }

.btn-convert, .btn-settle {
  font-size: .72rem; border: 1px solid #cfc4c5; background: #fff; padding: 3px 9px; cursor: pointer;
  transition: border-color .12s, color .12s;
}
.btn-convert:hover { border-color: #0050cc; color: #0050cc; }
.btn-settle { color: #4c4546; }
.btn-settle.active { border-color: #191c1d; color: #191c1d; font-weight: 600; }

.settle-tag { font-size: .68rem; font-weight: 600; color: #0050cc; width: fit-content; }
.settle-tag.done { color: #16a34a; }

.convert-panel, .settle-panel {
  margin-top: 16px; padding: 16px; border: 1px solid #e1e3e4; background: #f8f9fa;
}
.convert-panel { display: flex; gap: .5rem; align-items: center; }
.convert-panel select {
  padding: 6px 8px; border: 1px solid #cfc4c5; background: #fff; font-family: inherit;
}
.settle-panel p { font-size: .85rem; margin: 0 0 10px; color: #191c1d; }
.settle-panel input {
  width: 100%; padding: 8px; border: 1px solid #cfc4c5; margin-bottom: 10px; font-family: inherit;
}
.settle-preview { font-size: .85rem; color: #191c1d; margin-bottom: 12px; background: #fff; border: 1px solid #e1e3e4; padding: 10px; }
.highlight { color: #0050cc; }
.settle-panel__actions { display: flex; gap: .5rem; }
.panel-btn {
  flex: 1; padding: 9px; border: 1px solid #191c1d; cursor: pointer; font-weight: 600;
  background: #191c1d; color: #fff; font-family: inherit; transition: background .12s;
}
.panel-btn:hover { background: #0050cc; border-color: #0050cc; }
.panel-btn:disabled { background: #cfc4c5; border-color: #cfc4c5; cursor: not-allowed; }
.panel-btn--ghost { background: #fff; color: #4c4546; }
.panel-btn--ghost:hover { background: #f1f5f9; color: #4c4546; border-color: #cfc4c5; }
</style>