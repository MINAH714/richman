<!-- src/components/consumption/DonutChart.vue -->
<template>
  <div class="donut-wrap">
    <div class="donut-layout">
      <div class="donut-svg-wrap">
        <svg viewBox="0 0 200 200" width="180" height="180">
          <template v-for="(seg, i) in segments" :key="i">
            <circle
              class="donut-segment"
              cx="100" cy="100"
              :r="RADIUS"
              fill="transparent"
              :stroke="seg.color"
              :stroke-width="STROKE"
              :stroke-dasharray="`${seg.dash} ${CIRCUMFERENCE - seg.dash}`"
              :stroke-dashoffset="-seg.offset"
              :style="{ transition: 'stroke-dasharray .5s ease' }"
              @mouseenter="hovered = i"
              @mouseleave="hovered = null"
            />
          </template>
          <text x="100" y="95"  text-anchor="middle" class="donut-center-label">
            {{ hovered !== null ? categories[hovered]?.category_display : '총 지출' }}
          </text>
          <text x="100" y="116" text-anchor="middle" class="donut-center-amount">
            {{ hovered !== null
                ? categories[hovered]?.amount.toLocaleString()
                : totalExpense.toLocaleString() }}
          </text>
        </svg>
      </div>

      <ul class="donut-legend">
        <li
          v-for="(cat, i) in categories"
          :key="cat.category"
          class="donut-legend__item"
          :class="{ 'is-hovered': hovered === i }"
          @mouseenter="hovered = i"
          @mouseleave="hovered = null"
        >
          <span class="donut-legend__dot" :style="{ background: COLOR_MAP[cat.category] }" />
          <span class="donut-legend__name">{{ cat.category_display }}</span>
          <span class="donut-legend__ratio">{{ cat.ratio }}%</span>
          <span class="donut-legend__amount">{{ cat.amount.toLocaleString() }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  categories:    { type: Array,  default: () => [] },
  totalExpense:  { type: Number, default: 0 },
})

const hovered = ref(null)

const RADIUS      = 70
const STROKE      = 26
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

/* 모노톤 베이스 위에 한 가지 강조색(#0050cc)만 사용한 그레이스케일 팔레트 */
const COLOR_MAP = {
  food:         '#191c1d',
  cafe:         '#4c4546',
  transport:    '#0050cc',
  shopping:     '#7e7576',
  convenience:  '#9a9192',
  health:       '#b3aeb0',
  culture:      '#0266ff',
  telecom:      '#cfc4c5',
  subscription: '#003fa4',
  rent:         '#000000',
  transfer:     '#e1e3e4',
  etc:          '#d9dadb',
}

const segments = computed(() => {
  let offset = 0
  return props.categories.map(cat => {
    const dash = (cat.ratio / 100) * CIRCUMFERENCE
    const seg  = { color: COLOR_MAP[cat.category] || '#ccc', dash, offset }
    offset += dash
    return seg
  })
})
</script>

<style scoped>
.donut-wrap       { font-family: 'Inter', sans-serif; }
.donut-layout     { display: flex; gap: 24px; align-items: center; flex-wrap: wrap; }
.donut-center-label  { font-family: 'Geist', sans-serif; font-size: 11px; fill: #4c4546; letter-spacing: 0.04em; }
.donut-center-amount { font-family: 'Hanken Grotesk', sans-serif; font-size: 17px; fill: #191c1d; font-weight: 700; }
.donut-legend        { list-style: none; padding: 0; margin: 0; flex: 1; min-width: 180px; }
.donut-legend__item  {
  display: grid;
  grid-template-columns: 10px 1fr auto auto;
  gap: .5rem;
  align-items: center;
  padding: .4rem .2rem;
  border-bottom: 1px solid #e1e3e4;
  transition: background .12s;
}
.donut-legend__item.is-hovered { background: #f8f9fa; }
.donut-legend__dot    { width: 10px; height: 10px; border-radius: 50%; }
.donut-legend__name   { font-size: .82rem; color: #191c1d; font-weight: 500; }
.donut-legend__ratio  { font-family: 'Geist', sans-serif; font-size: .76rem; color: #4c4546; text-align: right; }
.donut-legend__amount { font-family: 'Hanken Grotesk', sans-serif; font-size: .8rem; color: #191c1d; font-weight: 700; text-align: right; min-width: 60px; }
</style>