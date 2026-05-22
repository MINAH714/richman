<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const username = ref('')
const password = ref('')

const router = useRouter()
const auth = useAuthStore()

const login = async () => {
  try {
    await auth.login(username.value, password.value)

    alert('로그인 성공')
    router.push('/')
  } catch (err) {
    alert('로그인 실패')
    console.log(err)
  }
}
</script>

<template>
  <div>
    <h1>로그인</h1>

    <input v-model="username" placeholder="아이디" />
    <input v-model="password" type="password" placeholder="비밀번호" />

    <button @click="login">
      로그인
    </button>
  </div>
</template>