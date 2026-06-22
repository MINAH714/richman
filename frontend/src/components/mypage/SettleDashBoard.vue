<!-- src/components/mypage/SettleDashboard.vue -->
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

    <h4 class="settle-section-title">⏳ 정산 대기중</h4>
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

    <h4 class="settle-section-title">✅ 정산 완료</h4>
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
  emit('settle-completed')   // 분석/캘린더도 같이 갱신 (완료 항목 삭제 시 전액 반영되어야 하므로)
}

const formatDate = (iso) => {
  const d = new Date(iso)
  return `${d.getMonth() + 1}월 ${d.getDate()}일`
}
</script>

<style scoped>
.settle-dash { background:#fff; border-radius:16px; padding:1.5rem; box-shadow:0 2px 12px rgba(0,0,0,.06); }
.settle-summary { display:flex; gap:1rem; margin-bottom:1.5rem; }
.summary-box { flex:1; background:#f8faff; border-radius:10px; padding:1rem; display:flex; flex-direction:column; gap:.3rem; }
.summary-label { font-size:.78rem; color:#94a3b8; }
.summary-amount { font-size:1.15rem; font-weight:700; }
.summary-amount.pending { color:#f59e0b; }
.summary-amount.done    { color:#16a34a; }

.settle-section-title { font-size:.9rem; font-weight:700; margin:1.2rem 0 .6rem; color:#374151; }
.settle-list { list-style:none; padding:0; margin:0; }
.settle-item {
  display:flex; justify-content:space-between; align-items:center;
  padding:.7rem 0; border-bottom:1px solid #f0f0f0;
}
.settle-item--done { opacity:.6; }
.settle-item__info { display:flex; flex-direction:column; gap:2px; }
.settle-item__top   { display:flex; align-items:center; gap:.5rem; }
.settle-item__desc { font-size:.9rem; font-weight:500; color:#333; }
.settle-item__date  { font-size:.72rem; color:#b0b8c4; background:#f4f6fa; padding:1px 6px; border-radius:4px; }
.settle-item__meta { font-size:.75rem; color:#94a3b8; }
.settle-item__right { display:flex; align-items:center; gap:.5rem; }
.settle-item__amount { font-weight:700; color:#3b6fd4; }
.btn-complete {
  font-size:.75rem; background:#3b6fd4; color:#fff; border:none;
  border-radius:6px; padding:5px 10px; cursor:pointer;
}
.btn-remove {
  font-size:.8rem; background:#f1f5f9; color:#94a3b8; border:none;
  border-radius:6px; width:24px; height:24px; cursor:pointer;
  display:flex; align-items:center; justify-content:center;
  transition: background .15s, color .15s;
}
.btn-remove:hover { background:#fef2f2; color:#ef4444; }
.settle-empty { font-size:.82rem; color:#94a3b8; padding:.5rem 0; }
</style>