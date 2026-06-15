<!-- frontend/src/App.vue -->
<template>
  <NavBar />
  <router-view />
  <ChatWidget />
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
import ChatWidget from '@/components/chatbot/ChatWidget.vue'
</script>