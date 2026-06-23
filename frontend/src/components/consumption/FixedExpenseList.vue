<!-- src/components/consumption/FixedExpenseList.vue -->
<template>
  <div class="fixed-wrap">
    <ul class="fixed-list">
      <li v-for="(item, index) in list" :key="index" class="fixed-item">
        <div class="fixed-item__left">
          <span class="fixed-item__tag">{{ CATEGORY_LABEL[item.category] || '기타' }}</span>
          <span class="fixed-item__name">{{ item.description }}</span>
        </div>
        <span class="fixed-item__amount">{{ item.amount.toLocaleString() }}원</span>
      </li>
    </ul>

    <div class="fixed-footer">
      <div class="fixed-footer__top">
        <span class="fixed-footer__label">고정지출 합계</span>
        <span class="fixed-footer__total">{{ total.toLocaleString() }}원</span>
      </div>
      <div class="fixed-bar">
        <div class="fixed-bar__fill" :style="{ width: fixedRatio + '%' }" />
      </div>
      <div class="fixed-footer__bottom">
        <span>가처분 소득 비중</span>
        <span class="fixed-ratio-label">{{ fixedRatio }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  list:         { type: Array,  default: () => [] },
  total:        { type: Number, default: 0 },
  totalExpense: { type: Number, default: 0 },
})

const fixedRatio = computed(() =>
  props.totalExpense
    ? Math.round(props.total / props.totalExpense * 100)
    : 0
)

const CATEGORY_LABEL = {
  rent:         '월세',
  telecom:      '통신',
  subscription: '구독',
  etc:          '기타',
}
</script>

<style scoped>
.fixed-wrap { font-family: 'Inter', sans-serif; }

.fixed-list {
  list-style: none;
  padding: 0;
  margin: 0 0 20px;
}
.fixed-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #e1e3e4;
}
.fixed-item__left { display: flex; align-items: center; gap: 10px; }
.fixed-item__tag {
  font-family: 'Geist', sans-serif;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.05em;
  color: #4c4546;
  border: 1px solid #cfc4c5;
  padding: 2px 7px;
  text-transform: uppercase;
}
.fixed-item__name { font-size: .88rem; color: #191c1d; font-weight: 500; }
.fixed-item__amount { font-size: .92rem; font-weight: 700; color: #191c1d; font-family: 'Hanken Grotesk', sans-serif; }

.fixed-footer { border-top: 1px solid #191c1d; padding-top: 16px; }
.fixed-footer__top { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; }
.fixed-footer__label {
  font-family: 'Geist', sans-serif;
  font-size: 11px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #4c4546;
}
.fixed-footer__total {
  font-family: 'Hanken Grotesk', sans-serif;
  font-size: 1.2rem;
  font-weight: 700;
  color: #191c1d;
}
.fixed-bar {
  height: 6px;
  background: #e1e3e4;
  margin-bottom: 8px;
  overflow: hidden;
}
.fixed-bar__fill {
  height: 100%;
  background: #191c1d;
  transition: width .4s ease;
}
.fixed-footer__bottom {
  display: flex;
  justify-content: space-between;
  font-size: .78rem;
  color: #4c4546;
}
.fixed-ratio-label { font-weight: 700; color: #0050cc; }
</style>