<template>
  <div class="fixed-wrap">
    <h3 class="section-title">
      고정 지출
      <span class="fixed-total">월 {{ total.toLocaleString() }}원</span>
    </h3>

    <ul class="fixed-list">
      <li v-for="item in list" :key="item.description" class="fixed-item">
        <div class="fixed-item__left">
          <span
            class="fixed-item__dot"
            :style="{ background: COLOR_MAP[item.category] || '#ccc' }"
          />
          <span class="fixed-item__name">{{ item.description }}</span>
        </div>
        <span class="fixed-item__amount">{{ item.amount.toLocaleString() }}원</span>
      </li>
    </ul>

    <div class="fixed-footer">
      <span>가처분 소득 비중</span>
      <div class="fixed-bar">
        <div
          class="fixed-bar__fill"
          :style="{ width: fixedRatio + '%', background: '#EF4444' }"
        />
      </div>
      <span class="fixed-ratio-label">{{ fixedRatio }}%</span>
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

const COLOR_MAP = {
  rent:         '#EF4444',
  telecom:      '#6366F1',
  subscription: '#8B5CF6',
  etc:          '#D1D5DB',
}
</script>

<style scoped>
.fixed-wrap      { background:#fff; border-radius:16px; padding:1.5rem; box-shadow:0 2px 12px rgba(0,0,0,.06); }
.section-title   { font-size:1rem; font-weight:700; margin-bottom:1rem; color:#333; display:flex; justify-content:space-between; align-items:center; }
.fixed-total     { font-size:.9rem; color:#EF4444; font-weight:700; }
.fixed-list      { list-style:none; padding:0; margin:0 0 1rem; }
.fixed-item      { display:flex; justify-content:space-between; align-items:center; padding:.5rem 0; border-bottom:1px solid #f5f5f5; }
.fixed-item__left   { display:flex; align-items:center; gap:.5rem; }
.fixed-item__dot    { width:10px; height:10px; border-radius:50%; }
.fixed-item__name   { font-size:.9rem; color:#444; }
.fixed-item__amount { font-size:.9rem; font-weight:600; color:#333; }
.fixed-footer    { margin-top:.5rem; }
.fixed-footer > span { font-size:.8rem; color:#888; }
.fixed-bar       { height:8px; background:#f0f0f0; border-radius:4px; margin:.4rem 0; overflow:hidden; }
.fixed-bar__fill { height:100%; border-radius:4px; transition:width .5s ease; }
.fixed-ratio-label { font-size:.85rem; font-weight:700; color:#EF4444; }
</style>