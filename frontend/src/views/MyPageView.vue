<!-- src/views/MyPageView.vue -->
<template>
  <div class="mypage">
    <div class="mypage-inner">
      <aside class="mypage-side">
        <ProfileTab />
      </aside>

      <main class="mypage-content">
        <nav class="mypage-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="mypage-tab"
            :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key"
          >
            {{ tab.icon }} {{ tab.label }}
          </button>
        </nav>

        <div class="mypage-panel">
          <CalendarTab v-if="activeTab === 'calendar'" />
          <InsightTab  v-else-if="activeTab === 'insight'" />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ProfileTab  from '@/components/mypage/ProfileTab.vue'
import CalendarTab from '@/components/mypage/CalendarTab.vue'
import InsightTab  from '@/components/mypage/InsightTab.vue'

const tabs = [
  { key: 'calendar', icon: '📅', label: '소비 캘린더' },
  { key: 'insight',  icon: '📊', label: '소비 분석' },
]
const activeTab = ref('calendar')
</script>

<style scoped>
.mypage       { background: #f0f6ff; min-height: calc(100vh - 56px); padding: 32px 24px; font-family: 'IBM Plex Mono', monospace; }
.mypage-inner { max-width: 1100px; margin: 0 auto; display: grid; grid-template-columns: 220px 1fr; gap: 24px; }
.mypage-tabs  { display: flex; gap: 8px; margin-bottom: 20px; }
.mypage-tab   {
  padding: 8px 16px; border-radius: 8px; border: 1px solid #e2ecf9;
  background: white; font-size: .85rem; font-weight: 600; color: #64748b;
  cursor: pointer; transition: all .15s; font-family: inherit;
}
.mypage-tab.active { background: #3b6fd4; color: white; border-color: #3b6fd4; }
.mypage-tab:hover:not(.active) { background: #f0f6ff; color: #3b6fd4; }
@media (max-width: 768px) { .mypage-inner { grid-template-columns: 1fr; } }
</style>