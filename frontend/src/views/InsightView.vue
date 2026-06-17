<!-- src/views/InsightView.vue -->
<template>
  <div class="insight-page">

    <div class="insight-header">
      <button @click="prevMonth">◀</button>
      <h2>{{ year }}년 {{ month }}월 소비 분석</h2>
      <button @click="nextMonth">▶</button>
    </div>

    <div v-if="loading" class="insight-loading">분석 중...</div>

    <div v-else class="insight-grid">
      <DonutChart
        :categories="data.categories"
        :total-expense="data.total_expense"
      />
      <MonthTrend :trend="trend" />
      <FixedExpenseList
        class="insight-fixed"
        :list="data.fixed?.list"
        :total="data.fixed?.total"
        :total-expense="data.total_expense"
      />
    </div>

  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { getInsight, getInsightTrend } from '@/api/consumption'
import DonutChart       from '@/components/consumption/DonutChart.vue'
import MonthTrend       from '@/components/consumption/MonthTrend.vue'
import FixedExpenseList from '@/components/consumption/FixedExpenseList.vue'

const today = new Date()
const year  = ref(today.getFullYear())
const month = ref(today.getMonth() + 1)

const data    = ref({ categories: [], total_expense: 0, fixed: { list: [], total: 0 } })
const trend   = ref([])
const loading = ref(false)

const fetchAll = async () => {
  loading.value = true
  const [insightRes, trendRes] = await Promise.all([
    getInsight(year.value, month.value),
    getInsightTrend(year.value, month.value),
  ])
  data.value  = insightRes.data
  trend.value = trendRes.data.trend
  loading.value = false
}

onMounted(fetchAll)
watch([year, month], fetchAll)

const prevMonth = () => {
  if (month.value === 1) { year.value--; month.value = 12 }
  else month.value--
}
const nextMonth = () => {
  if (month.value === 12) { year.value++; month.value = 1 }
  else month.value++
}
</script>

<style scoped>
.insight-page   { max-width: 900px; margin: 0 auto; padding: 1.5rem; }
.insight-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.insight-header h2 { font-size: 1.2rem; font-weight: 700; }
.insight-loading   { text-align: center; padding: 3rem; color: #888; }

/* 도넛 + 추이 나란히, 고정지출 아래 전체 너비 */
.insight-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.2rem;
}
.insight-fixed {
  grid-column: 1 / -1;   /* 2열 전체 차지 */
}
@media (max-width: 640px) {
  .insight-grid          { grid-template-columns: 1fr; }
  .insight-fixed         { grid-column: auto; }
}
</style>