<!-- src/components/mypage/InsightTab.vue -->
<template>
  <div class="insight-tab">
    <div class="insight-header">
      <button @click="prevMonth">◀</button>
      <h3>{{ year }}년 {{ month }}월</h3>
      <button @click="nextMonth">▶</button>
    </div>

    <p v-if="loading" class="loading">분석 중...</p>

    <div v-else class="insight-grid">
      <DonutChart :categories="data.categories" :total-expense="data.total_expense" />
      <MonthTrend :trend="trend" :selected-year="year" :selected-month="month" />
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
const data  = ref({ categories: [], total_expense: 0, fixed: { list: [], total: 0 } })
const trend = ref([])
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

const prevMonth = () => { if (month.value === 1) { year.value--; month.value = 12 } else month.value-- }
const nextMonth = () => { if (month.value === 12) { year.value++; month.value = 1 } else month.value++ }
</script>

<style scoped>
.insight-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; }
.insight-header h3 { font-size: 1rem; font-weight: 700; }
.insight-grid  { display: grid; grid-template-columns: 1fr 1fr; gap: 1.2rem; }
.insight-fixed { grid-column: 1 / -1; }
.loading       { text-align: center; padding: 3rem; color: #94a3b8; }
@media (max-width: 640px) { .insight-grid { grid-template-columns: 1fr; } }
</style>