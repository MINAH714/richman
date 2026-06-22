<!-- src/views/MyPageView.vue -->
<template>
  <div class="mypage">
    <div class="mypage-inner">

      <aside class="mypage-side">
        <ProfileTab />
      </aside>

      <main class="mypage-content">

        <div class="month-switcher">
          <button @click="prevMonth">◀</button>
          <h2>{{ year }}년 {{ month }}월</h2>
          <button @click="nextMonth">▶</button>
        </div>

        <!-- 1행: 캘린더 + 분석 가로 배치 -->
        <section class="mypage-section section-calendar">
          <h3 class="section-title">📅 소비 캘린더</h3>
          <CalendarTab
            :key="`cal-${refreshKey}`"
            :year="year"
            :month="month"
            @settle-changed="triggerRefresh"
          />
        </section>

        <section class="mypage-section section-insight">
          <h3 class="section-title">📊 소비 분석</h3>
          <InsightTab
            :key="`ins-${refreshKey}`"
            :year="year"
            :month="month"
            @data-loaded="onInsightLoaded"
          />
        </section>

        <!-- 2행: 고정지출 (전체 너비) -->
        <section class="mypage-section section-fixed">
          <h3 class="section-title">📌 고정 지출</h3>
          <FixedExpenseList
            :list="insightData.fixed?.list"
            :total="insightData.fixed?.total"
            :total-expense="insightData.total_expense"
          />
        </section>

        <!-- 3행: 정산 (전체 너비) -->
        <section class="mypage-section section-settle">
          <h3 class="section-title">🤝 정산</h3>
          <SettleDashBoard
            :key="`settle-${refreshKey}`"
            @settle-completed="triggerRefresh"
          />
        </section>

      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ProfileTab       from '@/components/mypage/ProfileTab.vue'
import CalendarTab      from '@/components/mypage/CalendarTab.vue'
import InsightTab       from '@/components/mypage/InsightTab.vue'
import SettleDashBoard  from '@/components/mypage/SettleDashBoard.vue'
import FixedExpenseList from '@/components/consumption/FixedExpenseList.vue'

const today = new Date()
const year  = ref(today.getFullYear())
const month = ref(today.getMonth() + 1)

const refreshKey  = ref(0)
const insightData = ref({ fixed: { list: [], total: 0 }, total_expense: 0 })

const triggerRefresh = () => {
  refreshKey.value++
}

const onInsightLoaded = (data) => {
  insightData.value = data
}

const prevMonth = () => { if (month.value === 1) { year.value--; month.value = 12 } else month.value-- }
const nextMonth = () => { if (month.value === 12) { year.value++; month.value = 1 } else month.value++ }
</script>

<style scoped>
.mypage       { background: #f0f6ff; min-height: calc(100vh - 56px); padding: 32px 24px; font-family: 'IBM Plex Mono', monospace; }
.mypage-inner { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 220px 1fr; gap: 24px; }

.mypage-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  align-items: start;
}

.month-switcher {
  grid-column: 1 / -1;
  display: flex; justify-content: center; align-items: center; gap: 1rem;
  margin-bottom: 0.5rem;
}
.month-switcher h2 { font-size: 1.15rem; font-weight: 700; color: #0f172a; }
.month-switcher button {
  background: white; border: 1px solid #e2ecf9; border-radius: 8px;
  width: 32px; height: 32px; cursor: pointer; font-size: .9rem;
}
.month-switcher button:hover { background: #f0f6ff; }

.mypage-section {
  background: white; border-radius: 16px; padding: 1.5rem;
  box-shadow: 0 2px 12px rgba(0,0,0,.06);
}
.section-title {
  font-size: 1rem; font-weight: 700; margin: 0 0 1.2rem; color: #0f172a;
}

/* 고정지출, 정산은 전체 너비 차지 */
.section-fixed,
.section-settle {
  grid-column: 1 / -1;
}

@media (max-width: 1024px) {
  .mypage-content { grid-template-columns: 1fr; }
  .section-fixed,
  .section-settle { grid-column: auto; }
}
@media (max-width: 768px) {
  .mypage-inner { grid-template-columns: 1fr; }
}
</style>