<!-- src/components/stocks/WatchlistCard.vue -->
<template>
  <div class="card">
    <!-- 종목 기본 정보 -->
    <div class="card-header">
      <div>
        <span class="symbol">{{ item.symbol }}</span>
        <span class="market-badge">{{ item.market }}</span>
      </div>
      <button class="btn-delete" @click="$emit('delete', item.id)" title="관심 종목 삭제">✕</button>
    </div>
    <div class="name">{{ item.name }}</div>

    <!-- 현재가 -->
    <div class="price-row">
      <span class="label">현재가</span>
      <span class="price">
        {{ item.current_price != null ? item.current_price.toLocaleString() : '불러오는 중...' }}
      </span>
    </div>

    <!-- 포트폴리오 정보 (입력한 경우에만 표시) -->
    <template v-if="item.portfolio">
      <div class="divider" />
      <div class="portfolio-row">
        <span class="label">보유 수량</span>
        <span>{{ item.portfolio.quantity }}</span>
      </div>
      <div class="portfolio-row">
        <span class="label">평균 매입가</span>
        <span>{{ Number(item.portfolio.average_price).toLocaleString() }}</span>
      </div>
      <div class="portfolio-row">
        <span class="label">수익률</span>
        <!-- 수익률 양수면 파란색, 음수면 빨간색 -->
        <span :class="profitClass">
          {{ item.portfolio.profit_rate != null ? item.portfolio.profit_rate + '%' : '-' }}
        </span>
      </div>
    </template>

    <!-- 하단 버튼 영역 -->
    <div class="card-footer">
      <button class="btn-portfolio" @click="$emit('edit-portfolio', item)">
        {{ item.portfolio ? '포트폴리오 수정' : '+ 포트폴리오 입력' }}
      </button>
      <!-- 차트 페이지 이동은 STEP 4(기능 2)에서 연결할 예정 -->
      <button class="btn-chart" @click="$emit('go-chart', item.symbol)">차트 보기 →</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  item: { type: Object, required: true }
})

defineEmits(['delete', 'edit-portfolio', 'go-chart'])

// 수익률 색상 클래스
const profitClass = computed(() => {
  const rate = props.item.portfolio?.profit_rate
  if (rate == null) return ''
  return rate >= 0 ? 'profit-positive' : 'profit-negative'
})
</script>

<style scoped>
.card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.card-header { display: flex; justify-content: space-between; align-items: center; }
.symbol { font-size: 18px; font-weight: 700; margin-right: 8px; }
.market-badge {
  font-size: 11px; background: #e8f0fe; color: #2563eb;
  padding: 2px 8px; border-radius: 99px;
}
.name { font-size: 13px; color: #666; }
.price-row { display: flex; justify-content: space-between; margin-top: 8px; }
.price { font-size: 16px; font-weight: 600; }
.label { font-size: 12px; color: #999; }
.divider { border-top: 1px solid #f0f0f0; margin: 8px 0; }
.portfolio-row { display: flex; justify-content: space-between; font-size: 13px; }
.profit-positive { color: #2563eb; font-weight: 700; }
.profit-negative { color: #ef4444; font-weight: 700; }
.btn-delete {
  background: none; border: none; cursor: pointer;
  color: #bbb; font-size: 16px; padding: 4px;
}
.btn-delete:hover { color: #ef4444; }
.card-footer { display: flex; gap: 8px; margin-top: 12px; }
.btn-portfolio {
  flex: 1; padding: 8px; border: 1px solid #2563eb;
  border-radius: 8px; color: #2563eb; background: #fff;
  cursor: pointer; font-size: 13px;
}
.btn-chart {
  flex: 1; padding: 8px; border: none;
  border-radius: 8px; background: #2563eb; color: #fff;
  cursor: pointer; font-size: 13px;
}
</style>