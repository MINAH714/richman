<template>
  <div class="trend-wrap">
    <h3 class="section-title">최근 3개월 지출 추이</h3>
    <div class="trend-bars">
      <div v-for="item in trend" :key="`${item.year}-${item.month}`" class="trend-bar-group">
        <span class="trend-amount">{{ (item.total / 10000).toFixed(0) }}만원</span>
        <div class="trend-bar-bg">
          <div
            class="trend-bar-fill"
            :style="{
              height: barHeight(item.total) + '%',
              background: isSelected(item) ? '#6c63ff' : '#c4b5fd'
            }"
          />
        </div>
        <span class="trend-label" :style="{ fontWeight: isSelected(item) ? 700 : 400 }">
          {{ item.month }}월
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  trend:        { type: Array,  default: () => [] },
  selectedYear: { type: Number, default: null },
  selectedMonth:{ type: Number, default: null },
})

const maxTotal  = computed(() => Math.max(...props.trend.map(t => t.total), 1))
const barHeight = (total) => Math.round(total / maxTotal.value * 100)
const isSelected = (item) =>
  item.year === props.selectedYear && item.month === props.selectedMonth
</script>

<style scoped>
.trend-wrap   { background:#fff; border-radius:16px; padding:1.5rem; box-shadow:0 2px 12px rgba(0,0,0,.06); }
.section-title { font-size:1rem; font-weight:700; margin-bottom:1.2rem; color:#333; }
.trend-bars   { display:flex; gap:1.5rem; align-items:flex-end; height:140px; padding-bottom:.5rem; }
.trend-bar-group { flex:1; display:flex; flex-direction:column; align-items:center; gap:.3rem; height:100%; justify-content:flex-end; }
.trend-amount { font-size:.75rem; color:#666; }
.trend-bar-bg { width:48px; background:#f0f0f0; border-radius:8px 8px 0 0; height:90%; display:flex; align-items:flex-end; overflow:hidden; }
.trend-bar-fill { width:100%; border-radius:8px 8px 0 0; transition:height .5s ease; }
.trend-label  { font-size:.85rem; color:#555; }
</style>