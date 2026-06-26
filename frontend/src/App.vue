<template>
  <div class="app-container">
    <NavBar />

    <main class="app-main">
      <router-view />
    </main>

    <TheFooter />

    <ChatWidget />
  </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
import TheFooter from '@/components/common/TheFooter.vue' // 🎯 푸터 임포트
import ChatWidget from '@/components/chatbot/ChatWidget.vue'
</script>

<style scoped>
/* 페이지가 짧아도 푸터가 항상 화면 최하단에 붙어있도록 유연한 레이아웃 구성 */
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-main {
  flex: 1; /* 남은 빈 영역을 채워 푸터를 아래로 밀어냅니다. */
  width: 100%;
}
</style>