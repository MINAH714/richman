<!-- src/components/mypage/InsightTab.vue -->
<template>
  <div class="insight-tab">
    <p v-if="loading" class="loading">불러오는 중</p>

    <div v-else class="insight-grid">
      <DonutChart :categories="data.categories" :total-expense="data.total_expense" />
      <MonthTrend :trend="trend" :selected-year="year" :selected-month="month" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { getInsight, getInsightTrend } from '@/api/consumption'
import DonutChart from '@/components/consumption/DonutChart.vue'
import MonthTrend from '@/components/consumption/MonthTrend.vue'

const props = defineProps({
  year:  { type: Number, required: true },
  month: { type: Number, required: true },
})

const emit = defineEmits(['data-loaded'])

const data    = ref({ categories: [], total_expense: 0, fixed: { list: [], total: 0 } })
const trend   = ref([])
const loading = ref(false)

const fetchAll = async () => {
  loading.value = true
  const [insightRes, trendRes] = await Promise.all([
    getInsight(props.year, props.month),
    getInsightTrend(props.year, props.month),
  ])
  data.value  = insightRes.data
  trend.value = trendRes.data.trend
  loading.value = false
  emit('data-loaded', data.value)
}
onMounted(fetchAll)
watch(() => [props.year, props.month], fetchAll)
</script>

<style scoped>
.insight-grid  { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.loading       {
  text-align: center; padding: 3rem; color: #4c4546;
  font-family: 'Geist', sans-serif; font-size: .8rem; letter-spacing: .04em;
}
@media (max-width: 640px) { .insight-grid { grid-template-columns: 1fr; } }
</style>