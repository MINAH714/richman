<!-- src/components/mypage/SpendingTab.vue -->
<template>
  <div class="spending-tab">

    <div class="month-switcher">
      <button class="month-btn" @click="prevMonth" aria-label="이전 달">‹</button>
      <h2 class="month-label">{{ year }}<span class="month-sep">/</span>{{ String(month).padStart(2, '0') }}</h2>
      <button class="month-btn" @click="nextMonth" aria-label="다음 달">›</button>
    </div>

    <div class="spending-grid">

      <section class="spending-section section-calendar">
        <h3 class="section-title"><span class="section-eyebrow">01</span>소비 캘린더</h3>
        <CalendarTab
          :key="`cal-${refreshKey}`"
          :year="year"
          :month="month"
          @settle-changed="triggerRefresh"
        />
      </section>

      <section class="spending-section section-insight">
        <h3 class="section-title"><span class="section-eyebrow">02</span>소비 분석</h3>
        <InsightTab
          :key="`ins-${year}-${month}-${refreshKey}`"
          :year="year"
          :month="month"
          @data-loaded="onInsightLoaded"
        />
      </section>

      <section class="spending-section section-fixed">
        <h3 class="section-title"><span class="section-eyebrow">03</span>고정 지출</h3>
        <FixedExpenseList
          :list="insightData.fixed?.list"
          :total="insightData.fixed?.total"
          :total-expense="insightData.total_expense"
        />
      </section>

      <section class="spending-section section-settle">
        <h3 class="section-title"><span class="section-eyebrow">04</span>정산</h3>
        <SettleDashBoard
          :key="`settle-${refreshKey}`"
          @settle-completed="triggerRefresh"
        />
      </section>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import CalendarTab      from '@/components/mypage/CalendarTab.vue'
import InsightTab       from '@/components/mypage/InsightTab.vue'
import SettleDashBoard  from '@/components/mypage/SettleDashBoard.vue'
import FixedExpenseList from '@/components/consumption/FixedExpenseList.vue'

const today = new Date()
const year  = ref(today.getFullYear())
const month = ref(today.getMonth() + 1)

const refreshKey  = ref(0)
const insightData = ref({ fixed: { list: [], total: 0 }, total_expense: 0 })

const triggerRefresh = () => { refreshKey.value++ }
const onInsightLoaded = (data) => { insightData.value = data }

const prevMonth = () => {
  insightData.value = { fixed: { list: [], total: 0 }, total_expense: 0 }
  if (month.value === 1) { year.value--; month.value = 12 }
  else month.value--
}
const nextMonth = () => {
  insightData.value = { fixed: { list: [], total: 0 }, total_expense: 0 }
  if (month.value === 12) { year.value++; month.value = 1 }
  else month.value++
}
</script>

<style scoped>
.spending-tab { font-family: 'Inter', sans-serif; }

.month-switcher {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e1e3e4;
}
.month-label {
  font-family: 'Hanken Grotesk', sans-serif;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: #191c1d;
  min-width: 140px;
  text-align: center;
}
.month-sep { color: #cfc4c5; font-weight: 500; margin: 0 4px; }
.month-btn {
  width: 36px;
  height: 36px;
  border: 1px solid #191c1d;
  background: #ffffff;
  color: #191c1d;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background .12s, color .12s;
  border-radius: 0;
}
.month-btn:hover { background: #191c1d; color: #ffffff; }

.spending-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}
.spending-section {
  background: #ffffff;
  border: 1px solid #e1e3e4;
  padding: 24px;
  border-radius: 0;
}
.section-title {
  font-family: 'Hanken Grotesk', sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
  margin: 0 0 20px;
  color: #191c1d;
  display: flex;
  align-items: baseline;
  gap: 10px;
}
.section-eyebrow {
  font-family: 'Geist', sans-serif;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.08em;
  color: #0050cc;
}

.section-fixed,
.section-settle { grid-column: 1 / -1; }

@media (max-width: 1024px) {
  .spending-grid { grid-template-columns: 1fr; }
  .section-fixed,
  .section-settle { grid-column: auto; }
}
</style>