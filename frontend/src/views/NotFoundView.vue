<template>
  <div class="min-h-[80vh] flex flex-col items-center justify-center bg-white text-center px-4 font-noto">
    <h1 class="text-9xl font-bold text-blue-600 mb-4 font-mono">404</h1>
    <h2 class="text-3xl font-semibold text-gray-900 mb-4">페이지를 찾을 수 없습니다</h2>
    <p class="text-gray-500 mb-8 max-w-md">
      요청하신 페이지가 사라졌거나, 잘못된 경로로 접근하셨습니다.
    </p>
    <router-link
      to="/"
      class="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
    >
      홈으로 돌아가기
    </router-link>
  </div>
</template>

<script setup>
// 특별한 로직이 필요 없는 정적 페이지입니다.
</script>