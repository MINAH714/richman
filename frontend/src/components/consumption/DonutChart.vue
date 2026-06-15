<template>
  <div class="donut-wrap">
    <h3 class="section-title">카테고리별 소비</h3>

    <div class="donut-layout">
      <!-- SVG 도넛 차트 -->
      <div class="donut-svg-wrap">
        <svg viewBox="0 0 200 200" width="200" height="200">
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

          <!-- 중앙 텍스트 -->
          <text x="100" y="95"  text-anchor="middle" class="donut-center-label">
            {{ hovered !== null ? categories[hovered]?.category_display : '총 지출' }}
          </text>
          <text x="100" y="115" text-anchor="middle" class="donut-center-amount">
            {{ hovered !== null
                ? categories[hovered]?.amount.toLocaleString() + '원'
                : totalExpense.toLocaleString() + '원' }}
          </text>
        </svg>
      </div>

      <!-- 범례 -->
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
          <span class="donut-legend__amount">{{ cat.amount.toLocaleString() }}원</span>
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
const STROKE      = 28
const CIRCUMFERENCE = 2 * Math.PI * RADIUS   // ≈ 439.8

const COLOR_MAP = {
  food:         '#FF6B6B',
  cafe:         '#A78BFA',
  transport:    '#34D399',
  shopping:     '#F59E0B',
  convenience:  '#60A5FA',
  health:       '#10B981',
  culture:      '#EC4899',
  telecom:      '#6366F1',
  subscription: '#8B5CF6',
  rent:         '#EF4444',
  transfer:     '#9CA3AF',
  etc:          '#D1D5DB',
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
.donut-wrap       { background:#fff; border-radius:16px; padding:1.5rem; box-shadow:0 2px 12px rgba(0,0,0,.06); }
.section-title    { font-size:1rem; font-weight:700; margin-bottom:1.2rem; color:#333; }
.donut-layout     { display:flex; gap:2rem; align-items:center; flex-wrap:wrap; }
.donut-center-label  { font-size:13px; fill:#888; }
.donut-center-amount { font-size:15px; fill:#222; font-weight:700; }
.donut-legend        { list-style:none; padding:0; margin:0; flex:1; min-width:180px; }
.donut-legend__item  {
  display:grid;
  grid-template-columns:12px 1fr auto auto;
  gap:.4rem;
  align-items:center;
  padding:.35rem .4rem;
  border-radius:6px;
  cursor:default;
  transition:background .15s;
}
.donut-legend__item.is-hovered { background:#f5f3ff; }
.donut-legend__dot    { width:12px; height:12px; border-radius:50%; }
.donut-legend__name   { font-size:.85rem; color:#444; }
.donut-legend__ratio  { font-size:.8rem; color:#888; text-align:right; }
.donut-legend__amount { font-size:.8rem; color:#333; font-weight:600; text-align:right; min-width:70px; }
</style>