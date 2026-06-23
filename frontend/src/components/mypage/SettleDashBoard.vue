<!-- src/components/mypage/SettleDashBoard.vue -->
<template>
  <div class="settle-dash">
    <div class="settle-summary">
      <div class="summary-box">
        <span class="summary-label">받을 돈 (대기중)</span>
        <span class="summary-amount pending">{{ data.pending?.total?.toLocaleString() || 0 }}원</span>
      </div>
      <div class="summary-box">
        <span class="summary-label">정산 완료</span>
        <span class="summary-amount done">{{ data.settled?.total?.toLocaleString() || 0 }}원</span>
      </div>
    </div>

    <h4 class="settle-section-title">정산 대기중</h4>
    <ul class="settle-list" v-if="data.pending?.list?.length">
      <li v-for="tx in data.pending.list" :key="tx.id" class="settle-item">
        <div class="settle-item__info">
          <div class="settle-item__top">
            <span class="settle-item__desc">{{ tx.description }}</span>
            <span class="settle-item__date">{{ formatDate(tx.transacted_at) }}</span>
          </div>
          <span class="settle-item__meta">
            총 {{ tx.amount.toLocaleString() }}원 ÷ {{ tx.settle_people_count }}명
          </span>
        </div>
        <div class="settle-item__right">
          <span class="settle-item__amount">+{{ tx.settle_amount?.toLocaleString() }}원</span>
          <button class="btn-complete" @click="markComplete(tx)">받았어요</button>
          <button class="btn-remove" @click="removeItem(tx)">✕</button>
        </div>
      </li>
    </ul>
    <p v-else class="settle-empty">정산 대기중인 항목이 없어요.</p>

    <h4 class="settle-section-title">정산 완료</h4>
    <ul class="settle-list" v-if="data.settled?.list?.length">
      <li v-for="tx in data.settled.list" :key="tx.id" class="settle-item settle-item--done">
        <div class="settle-item__info">
          <div class="settle-item__top">
            <span class="settle-item__desc">{{ tx.description }}</span>
            <span class="settle-item__date">{{ formatDate(tx.transacted_at) }}</span>
          </div>
          <span class="settle-item__meta">
            총 {{ tx.amount.toLocaleString() }}원 ÷ {{ tx.settle_people_count }}명
          </span>
        </div>
        <div class="settle-item__right">
          <span class="settle-item__amount">+{{ tx.settle_amount?.toLocaleString() }}원</span>
          <button class="btn-remove" @click="removeItem(tx)">✕</button>
        </div>
      </li>
    </ul>
    <p v-else class="settle-empty">완료된 정산이 없어요.</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getSettleDashboard, completeSettle, removeSettle } from '@/api/consumption'

const emit = defineEmits(['settle-completed'])

const data = ref({ pending: { list: [], total: 0 }, settled: { list: [], total: 0 } })

const fetchDashboard = async () => {
  const { data: res } = await getSettleDashboard()
  data.value = res
}

onMounted(fetchDashboard)

const markComplete = async (tx) => {
  await completeSettle(tx.id)
  await fetchDashboard()
  emit('settle-completed')
}

const removeItem = async (tx) => {
  if (!confirm(`"${tx.description}" 정산을 삭제할까요? 일반 지출로 되돌아갑니다.`)) return
  await removeSettle(tx.id)
  await fetchDashboard()
  emit('settle-completed')
}

const formatDate = (iso) => {
  const d = new Date(iso)
  return `${d.getMonth() + 1}.${d.getDate()}`
}
</script>

<style scoped>
.settle-dash { font-family: 'Inter', sans-serif; }

.settle-summary { display: flex; gap: 1px; margin-bottom: 24px; background: #e1e3e4; border: 1px solid #e1e3e4; }
.summary-box { flex: 1; background: #ffffff; padding: 16px; display: flex; flex-direction: column; gap: 6px; }
.summary-label {
  font-family: 'Geist', sans-serif;
  font-size: 10px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #4c4546;
}
.summary-amount { font-family: 'Hanken Grotesk', sans-serif; font-size: 1.3rem; font-weight: 700; }
.summary-amount.pending { color: #191c1d; }
.summary-amount.done    { color: #0050cc; }

.settle-section-title {
  font-family: 'Geist', sans-serif;
  font-size: 11px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  font-weight: 600;
  margin: 20px 0 10px;
  color: #4c4546;
  border-bottom: 1px solid #191c1d;
  padding-bottom: 8px;
}
.settle-list { list-style: none; padding: 0; margin: 0; }
.settle-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 0; border-bottom: 1px solid #e1e3e4;
}
.settle-item--done { opacity: .55; }
.settle-item__info { display: flex; flex-direction: column; gap: 3px; }
.settle-item__top   { display: flex; align-items: center; gap: 8px; }
.settle-item__desc { font-size: .88rem; font-weight: 600; color: #191c1d; }
.settle-item__date  { font-family: 'Geist', sans-serif; font-size: 10px; color: #4c4546; border: 1px solid #cfc4c5; padding: 1px 6px; }
.settle-item__meta { font-size: .76rem; color: #4c4546; }
.settle-item__right { display: flex; align-items: center; gap: 10px; }
.settle-item__amount { font-family: 'Hanken Grotesk', sans-serif; font-weight: 700; color: #0050cc; }
.btn-complete {
  font-size: .76rem; background: #191c1d; color: #fff; border: none;
  padding: 7px 12px; cursor: pointer; font-weight: 600; font-family: 'Inter', sans-serif;
  transition: background .12s;
}
.btn-complete:hover { background: #0050cc; }
.btn-remove {
  font-size: .8rem; background: #ffffff; color: #4c4546; border: 1px solid #cfc4c5;
  width: 26px; height: 26px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: border-color .12s, color .12s;
}
.btn-remove:hover { border-color: #ba1a1a; color: #ba1a1a; }
.settle-empty { font-size: .82rem; color: #4c4546; padding: 16px 0; }
</style>