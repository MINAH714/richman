// frontend/src/components/consumption/DonutChart.vue
<template>
  <div class="donut-wrap">
    <div class="donut-layout">
      <div class="donut-svg-wrap">
        <svg viewBox="0 0 200 200" :width="size" :height="size">
          
          <g transform="rotate(-90 100 100)">
            <template v-for="(seg, i) in segments" :key="'circle-'+i">
              <circle
                class="donut-segment"
                cx="100" cy="100"
                :r="RADIUS"
                fill="transparent"
                :stroke="seg.color"
                :stroke-width="STROKE"
                :stroke-dasharray="`${seg.dash} ${CIRCUMFERENCE - seg.dash}`"
                :stroke-dashoffset="-seg.offset"
                :style="{ 
                  transition: 'stroke-dasharray .5s ease, opacity 0.2s',
                  opacity: hovered !== null && hovered !== i ? 0.3 : 1 
                }"
                @mouseenter="hovered = i"
                @mouseleave="hovered = null"
              />
            </template>
          </g>

          <template v-for="(seg, i) in segments" :key="'text-'+i">
            <text
              v-if="seg.showLabel"
              :x="seg.textX"
              :y="seg.textY"
              text-anchor="middle"
              alignment-baseline="middle"
              class="donut-segment-text"
              :style="{ opacity: hovered !== null && hovered !== i ? 0.3 : 1 }"
            >
              {{ showRatioInLabel ? `${seg.category_display} ${seg.ratio}%` : seg.category_display }}
            </text>
          </template>

          <text x="100" y="95"  text-anchor="middle" class="donut-center-label">
            {{ hovered !== null ? categories[hovered]?.category_display : centerLabel }}
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

// ⭐ [수정] colorMap, centerLabel props 추가 (기본값은 기존 동작과 100% 동일하게 유지)
const props = defineProps({
  categories:       { type: Array,  default: () => [] },
  totalExpense:     { type: Number, default: 0 },
  colorMap:         { type: Object, default: null },
  centerLabel:      { type: String, default: '총 지출' },
  showRatioInLabel: { type: Boolean, default: false },   // ⭐ [신규 추가]
  size:             { type: Number, default: 180 },        // ⭐ [신규 추가] 기존 기본값(180)과 동일
})

const hovered = ref(null)

const RADIUS      = 70
const STROKE      = 26
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

// 기존 소비 카테고리용 기본 컬러맵 (그대로 유지, 이름만 DEFAULT_COLOR_MAP으로 명확화)
const DEFAULT_COLOR_MAP = {   // ⭐ [수정] COLOR_MAP → DEFAULT_COLOR_MAP으로 이름 변경
  food:         '#FF6B6B',
  cafe:         '#FF9F43',
  transport:    '#54A0FF',
  shopping:     '#1DD1A1',
  convenience:  '#F368E0',
  health:       '#10AC84',
  culture:      '#5F27CD',
  telecom:      '#0ABDE3',
  subscription: '#2E86DE',
  rent:         '#341F97',
  transfer:     '#EE5253',
  etc:          '#8395A7',
}

// ⭐ [신규 추가] colorMap prop이 있으면 그걸 쓰고, 없으면 기존 기본값 사용
const COLOR_MAP = computed(() => props.colorMap || DEFAULT_COLOR_MAP)


const segments = computed(() => {
  let offset = 0
  let currentRatio = 0

  return props.categories.map(cat => {
    const dash = (cat.ratio / 100) * CIRCUMFERENCE
    const seg  = { 
      ...cat,
      color: COLOR_MAP.value[cat.category] || COLOR_MAP.value.etc,   // ⭐ [수정]
      dash, 
      offset 
    }

    // 🔧 추가: 텍스트 위치 계산 (해당 조각의 중간 각도를 라디안으로 계산)
    const midRatio = currentRatio + (cat.ratio / 2)
    // -90도(12시 방향)를 기준으로 라디안 계산
    const angle = (midRatio / 100) * 2 * Math.PI - (Math.PI / 2)
    
    // 반지름 70(STROKE 중심) 위치에 x, y 좌표 산출
    seg.textX = 100 + RADIUS * Math.cos(angle)
    seg.textY = 100 + RADIUS * Math.sin(angle)
    // 글씨가 서로 겹치는 것을 방지하기 위해 5% 이상일 때만 텍스트 렌더링
    seg.showLabel = cat.ratio >= 5

    offset += dash
    currentRatio += cat.ratio

    return seg
  })
})
</script>

<style scoped>
.donut-wrap       { font-family: 'Inter', sans-serif; }
.donut-layout     { display: flex; gap: 24px; align-items: center; flex-wrap: wrap; }

.donut-segment { cursor: pointer; }
/* 🔧 추가: 도넛 조각 위 텍스트 스타일 */
.donut-segment-text {
  font-family: 'Geist', sans-serif;
  font-size: 11px;
  font-weight: 600;
  fill: #ffffff;
  pointer-events: none; /* 텍스트 위에 마우스를 올려도 뒷 배경 circle의 hover 유지 */
  text-shadow: 0px 1px 3px rgba(0, 0, 0, 0.4); /* 밝은 색상 위에서도 잘 보이도록 그림자 추가 */
  transition: opacity 0.2s;
}

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
  cursor: pointer;
}
.donut-legend__item.is-hovered { background: #f8f9fa; }
.donut-legend__dot    { width: 10px; height: 10px; border-radius: 50%; }
.donut-legend__name   { font-size: .82rem; color: #191c1d; font-weight: 500; }
.donut-legend__ratio  { font-family: 'Geist', sans-serif; font-size: .76rem; color: #4c4546; text-align: right; }
.donut-legend__amount { font-family: 'Hanken Grotesk', sans-serif; font-size: .8rem; color: #191c1d; font-weight: 700; text-align: right; min-width: 60px; }
</style>