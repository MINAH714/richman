// frontend/src/components/consumption/DonutChart.vue
<template>
  <div class="donut-wrap">
    <div class="donut-layout">
      <div class="donut-svg-wrap">
        <svg viewBox="0 0 200 200" width="180" height="180">
          
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
              {{ seg.category_display }}
            </text>
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

/* 🔧 변경: 시인성을 높이기 위해 뚜렷하게 구분되는 비비드/파스텔 혼합 컬러로 변경 */
const COLOR_MAP = {
  food:         '#FF6B6B', // 빨강 (식비)
  cafe:         '#FF9F43', // 주황 (카페/간식)
  transport:    '#54A0FF', // 파랑 (교통)
  shopping:     '#1DD1A1', // 민트 (쇼핑)
  convenience:  '#F368E0', // 핑크 (편의점)
  health:       '#10AC84', // 녹색 (의료/건강)
  culture:      '#5F27CD', // 보라 (문화)
  telecom:      '#0ABDE3', // 시안 (통신)
  subscription: '#2E86DE', // 진파랑 (구독)
  rent:         '#341F97', // 네이비 (주거)
  transfer:     '#EE5253', // 짙은 빨강 (이체)
  etc:          '#8395A7', // 회색 (기타)
}

const segments = computed(() => {
  let offset = 0
  let currentRatio = 0

  return props.categories.map(cat => {
    const dash = (cat.ratio / 100) * CIRCUMFERENCE
    const seg  = { 
      ...cat,
      color: COLOR_MAP[cat.category] || COLOR_MAP.etc, 
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