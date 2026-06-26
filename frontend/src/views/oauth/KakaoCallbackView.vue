<template>
  <div>카카오 로그인 처리 중...</div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/axios'

const router = useRouter()
const authStore = useAuthStore()

onMounted(async () => {
  const code = new URLSearchParams(window.location.search).get('code')
  
  if (!code) {
    router.push('/login')
    return
  }

  try {
    const response = await api.post('/api/accounts/kakao/login/', { code })
    const { access, refresh } = response.data

    authStore.setTokens(access, refresh)
    // await authStore.fetchUser() ← 제거

    router.push('/')
  } catch (error) {
    console.error('카카오 로그인 실패:', error)
    router.push('/login')
  }
})
</script>