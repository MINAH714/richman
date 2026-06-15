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
          </div>
          <div class="modal__item-right">
            <span class="modal__amount">{{ tx.amount.toLocaleString() }}원</span>
            <!-- 이체 건: 지출로 전환 버튼 -->
            <button
              v-if="tx.transaction_type === 'transfer'"
              class="btn-convert"
              @click="openConvert(tx)"
            >
              지출로 변경
            </button>
          </div>
        </li>
      </ul>

      <!-- 카테고리 선택 드롭다운 -->
      <div v-if="convertTarget" class="convert-panel">
        <p>카테고리 선택</p>
        <select v-model="newCategory">
          <option v-for="c in CATEGORIES" :key="c.value" :value="c.value">
            {{ c.label }}
          </option>
        </select>
        <button @click="confirmConvert">확인</button>
        <button @click="convertTarget = null">취소</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDayDetail, updateCategory } from '@/api/consumption'
import CategoryBadge from './CategoryBadge.vue'

const props = defineProps({ date: String })
const emit  = defineEmits(['close'])

const transactions = ref([])
const total        = ref(0)
const convertTarget = ref(null)
const newCategory   = ref('food')

const CATEGORIES = [
  { value:'food',        label:'식비' },
  { value:'cafe',        label:'카페' },
  { value:'transport',   label:'교통' },
  { value:'shopping',    label:'쇼핑' },
  { value:'convenience', label:'편의점' },
  { value:'health',      label:'의료/건강' },
  { value:'culture',     label:'문화/여가' },
  { value:'etc',         label:'기타' },
]

onMounted(async () => {
  const { data } = await getDayDetail(props.date)
  transactions.value = data.transactions
  total.value        = data.total
})

const formatTime = (iso) =>
  new Date(iso).toLocaleTimeString('ko-KR', { hour:'2-digit', minute:'2-digit' })

const openConvert = (tx) => {
  convertTarget.value = tx
  newCategory.value   = 'food'
}

const confirmConvert = async () => {
  await updateCategory(convertTarget.value.id, newCategory.value)
  // 로컬 상태 즉시 반영
  const tx = transactions.value.find(t => t.id === convertTarget.value.id)
  if (tx) {
    tx.transaction_type = 'expense'
    tx.category         = newCategory.value
    tx.category_display = CATEGORIES.find(c => c.value === newCategory.value)?.label
    if (tx.transaction_type !== 'transfer') total.value += tx.amount
  }
  convertTarget.value = null
}
</script>

<style scoped>
.modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,.4); display:flex; align-items:center; justify-content:center; z-index:100; }
.modal { background:#fff; border-radius:16px; width:480px; max-height:80vh; overflow-y:auto; padding:1.5rem; }
.modal__header { display:flex; justify-content:space-between; align-items:center; margin-bottom:.5rem; }
.modal__total  { color:#6c63ff; font-weight:700; font-size:1.1rem; margin-bottom:1rem; }
.modal__list   { list-style:none; padding:0; margin:0; }
.modal__item   { display:flex; justify-content:space-between; align-items:center; padding:.7rem 0; border-bottom:1px solid #f0f0f0; }
.modal__item-left { display:flex; flex-direction:column; gap:2px; }
.modal__time   { font-size:.75rem; color:#aaa; }
.modal__desc   { font-size:.95rem; font-weight:500; }
.modal__amount { font-weight:700; }
.btn-convert   { font-size:.75rem; background:#f0f4ff; border:none; border-radius:6px; padding:3px 8px; cursor:pointer; color:#6c63ff; }
.convert-panel { margin-top:1rem; padding:1rem; background:#f9f9f9; border-radius:8px; display:flex; gap:.5rem; align-items:center; }
</style>