<template>
  <div>네이버 로그인 처리 중...</div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

onMounted(() => {
  const params = new URLSearchParams(window.location.search)
  const access = params.get('access')
  const refresh = params.get('refresh')

  if (!access || !refresh) {
    router.push('/login')
    return
  }

  authStore.setTokens(access, refresh)
  router.push('/')
})
</script>