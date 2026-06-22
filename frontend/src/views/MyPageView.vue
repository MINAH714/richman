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

        <section class="mypage-section section-calendar">
          <h3 class="section-title">📅 소비 캘린더</h3>
          <CalendarTab :year="year" :month="month" />
        </section>

        <section class="mypage-section section-insight">
          <h3 class="section-title">📊 소비 분석</h3>
          <InsightTab :year="year" :month="month" />
        </section>

        <section class="mypage-section section-settle">
          <h3 class="section-title">🤝 정산</h3>
          <SettleDashBoard />
        </section>

      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ProfileTab      from '@/components/mypage/ProfileTab.vue'
import CalendarTab     from '@/components/mypage/CalendarTab.vue'
import InsightTab      from '@/components/mypage/InsightTab.vue'
import SettleDashBoard from '@/components/mypage/SettleDashBoard.vue'

const today = new Date()
const year  = ref(today.getFullYear())
const month = ref(today.getMonth() + 1)

const prevMonth = () => { if (month.value === 1) { year.value--; month.value = 12 } else month.value-- }
const nextMonth = () => { if (month.value === 12) { year.value++; month.value = 1 } else month.value++ }
</script>

<style scoped>
.mypage       { background: #f0f6ff; min-height: calc(100vh - 56px); padding: 32px 24px; font-family: 'IBM Plex Mono', monospace; }
.mypage-inner { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 220px 1fr; gap: 24px; }

/* 🎯 메인 콘텐츠 영역을 2열 그리드로 변환 */
.mypage-content {
  display: grid;
  grid-template-columns: 1fr 1fr; /* 50% 50% 반반 분할 */
  gap: 20px;
  align-items: start;
}

/* 월 선택 스위처는 2열을 통째로 다 차지하도록 설정 */
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

/* 공통 섹션 스타일 (원래 마진-텀 지우고 그리드 갭으로 제어) */
.mypage-section {
  background: white; border-radius: 16px; padding: 1.5rem;
  box-shadow: 0 2px 12px rgba(0,0,0,.06);
  margin-bottom: 0; /* 기존 마진 삭제 */
}
.section-title {
  font-size: 1rem; font-weight: 700; margin: 0 0 1.2rem; color: #0f172a;
}

/* 🎯 정산 섹션만 아래에서 가로 2열을 다 채우도록 지정 */
.section-settle {
  grid-column: 1 / -1;
}

/* 태블릿이나 모바일 환경에서는 다시 세로로 한 줄씩 떨어지도록 방어 코드 추가 */
@media (max-width: 1024px) {
  .mypage-content {
    grid-template-columns: 1fr;
  }
  .section-settle {
    grid-column: auto;
  }
}

@media (max-width: 768px) { .mypage-inner { grid-template-columns: 1fr; } }
</style>