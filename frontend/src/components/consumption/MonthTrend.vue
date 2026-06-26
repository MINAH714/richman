<!-- src/components/consumption/MonthTrend.vue -->
<template>
  <div class="trend-wrap">
    
    <div class="trend-header">
      <span class="trend-subtitle">(1일 ~ {{ currentDay }}일 기준 비교)</span>
    </div>

    <div class="trend-bars">
      <div v-for="item in trend" :key="`${item.year}-${item.month}`" class="trend-bar-group">
        <span class="trend-amount" :class="{ 'is-selected': isSelected(item) }">
          {{ (item.total / 10000).toFixed(0) }}만
        </span>
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

// 오늘 날짜 일(day)을 가져와서 UI에 렌더링
const currentDay = new Date().getDate()

const maxTotal  = computed(() => {
  const max = Math.max(...props.trend.map(t => t.total))
  return max > 0 ? max : 1 // 0으로 나누기 방지
})

const barHeight = (total) => Math.round((total / maxTotal.value) * 100)

const isSelected = (item) =>
  item.year === props.selectedYear && item.month === props.selectedMonth
</script>

<style scoped>
.trend-wrap { 
  font-family: 'Inter', sans-serif; 
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

.trend-header {
  text-align: right;
  padding-right: 10px;
}

.trend-subtitle {
  font-family: 'Geist', sans-serif;
  font-size: 0.75rem;
  color: #8395A7;
  font-weight: 500;
}

.trend-bars { 
  display: flex; 
  gap: 32px; /* 막대 사이 간격 확장 */
  align-items: flex-end; 
  height: 150px; 
  justify-content: center;
  padding-bottom: 4px; 
}

.trend-bar-group {
  width: 42px; /* 막대 너비 고정 */
  display: flex; 
  flex-direction: column; 
  align-items: center; 
  gap: 8px;
  height: 100%; 
  justify-content: flex-end;
}

.trend-amount { 
  font-family: 'Geist', sans-serif; 
  font-size: 0.75rem; 
  color: #8395A7; 
  font-weight: 500;
  transition: color 0.3s;
}

.trend-amount.is-selected {
  color: #3B82F6;
  font-weight: 700;
}

/* 🔧 기존 로딩 바 느낌을 주는 배경을 부드러운 슬레이트 그레이로 변경 */
.trend-bar-bg {
  width: 100%; 
  background: #F1F5F9; 
  height: 100%;
  display: flex; 
  align-items: flex-end; 
  border-radius: 6px;
  overflow: hidden;
}

/* 🔧 채워지는 바도 모서리를 둥글게 하고 세련된 톤으로 변경 */
.trend-bar-fill {
  width: 100%; 
  background: #94A3B8; 
  border-radius: 6px;
  transition: height 0.5s cubic-bezier(0.4, 0, 0.2, 1), background 0.3s;
}

.trend-bar-fill.is-selected { 
  background: #3B82F6; /* 선택된 달은 프로젝트 메인 컬러(블루) 계열로 강조 */
}

.trend-label {
  font-family: 'Hanken Grotesk', sans-serif;
  font-size: 0.85rem; 
  color: #475569; 
  font-weight: 600;
}

.trend-label.is-selected { 
  color: #3B82F6; 
  font-weight: 700; 
}
</style>