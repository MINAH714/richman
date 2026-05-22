<script setup>
import { onMounted, ref } from 'vue'
import api from '@/api/axios'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const user = ref(null)

const logout = () => {
  auth.logout()
}

onMounted(async () => {
  try {
    const res = await api.get('/api/accounts/me/')

    user.value = res.data
  } catch (err) {
    console.log(err)
  }
})
</script>

<template>
  <div>
    <h1>홈 화면</h1>

    <div v-if="user">
      <p>아이디: {{ user.username }}</p>
      <p>닉네임: {{ user.nickname }}</p>
    </div>

    <button @click="logout">
      로그아웃
    </button>
  </div>
</template>