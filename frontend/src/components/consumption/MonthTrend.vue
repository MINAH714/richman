<!-- src/components/consumption/MonthTrend.vue -->
<template>
  <div class="trend-wrap">
    <div class="trend-bars">
      <div v-for="item in trend" :key="`${item.year}-${item.month}`" class="trend-bar-group">
        <span class="trend-amount">{{ (item.total / 10000).toFixed(0) }}만</span>
        <div class="trend-bar-bg">
          <div
            class="trend-bar-fill"
            :class="{ 'is-selected': isSelected(item) }"
            :style="{ height: barHeight(item.total) + '%' }"
          />
        </div>
        <span class="trend-label" :class="{ 'is-selected': isSelected(item) }">
          {{ item.month }}월
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  trend:         { type: Array,  default: () => [] },
  selectedYear:  { type: Number, default: null },
  selectedMonth: { type: Number, default: null },
})

const maxTotal  = computed(() => Math.max(...props.trend.map(t => t.total), 1))
const barHeight = (total) => Math.round(total / maxTotal.value * 100)
const isSelected = (item) =>
  item.year === props.selectedYear && item.month === props.selectedMonth
</script>

<style scoped>
.trend-wrap   { font-family: 'Inter', sans-serif; }
.trend-bars   { display: flex; gap: 20px; align-items: flex-end; height: 150px; padding-bottom: 4px; }
.trend-bar-group {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px;
  height: 100%; justify-content: flex-end;
}
.trend-amount { font-family: 'Geist', sans-serif; font-size: .72rem; color: #4c4546; }
.trend-bar-bg {
  width: 100%; max-width: 48px; background: #e1e3e4; height: 92%;
  display: flex; align-items: flex-end; overflow: hidden;
}
.trend-bar-fill {
  width: 100%; background: #cfc4c5; transition: height .5s ease, background .2s;
}
.trend-bar-fill.is-selected { background: #191c1d; }
.trend-label {
  font-family: 'Hanken Grotesk', sans-serif;
  font-size: .82rem; color: #4c4546; font-weight: 500;
}
.trend-label.is-selected { color: #0050cc; font-weight: 700; }
</style>