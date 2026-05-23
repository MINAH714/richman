<script setup>
import { ref } from 'vue'
import axios from '@/api/axios'

// 기존 로그인 상태
const username = ref('')
const password = ref('')

// 기존 일반 로그인
const login = async () => {
  try {
    const response = await axios.post('/accounts/login/', {
      username: username.value,
      password: password.value,
    })

    console.log(response.data)
  } catch (error) {
    console.error(error)
  }
}

// Google OAuth 로그인
const googleLogin = () => {
  const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID

  const REDIRECT_URI =
    'http://localhost:5173/oauth/google/callback'

  const scope = 'email profile'

  const googleURL =
    `https://accounts.google.com/o/oauth2/v2/auth` +
    `?client_id=${CLIENT_ID}` +
    `&redirect_uri=${REDIRECT_URI}` +
    `&response_type=code` +
    `&scope=${scope}`

  window.location.href = googleURL
}
</script>

<template>
  <div class="login-container">
    <h1>로그인</h1>

    <!-- 일반 로그인 -->
    <form @submit.prevent="login">
      <div>
        <input
          v-model="username"
          type="text"
          placeholder="아이디"
        />
      </div>

      <div>
        <input
          v-model="password"
          type="password"
          placeholder="비밀번호"
        />
      </div>

      <button type="submit">
        로그인
      </button>
    </form>

    <hr />

    <!-- 소셜 로그인 -->
    <div class="social-login">
      <button
        type="button"
        @click="googleLogin"
      >
        Google 로그인
      </button>

      <button type="button">
        Kakao 로그인
      </button>

      <button type="button">
        Naver 로그인
      </button>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  width: 300px;
  margin: 100px auto;
}

input {
  width: 100%;
  padding: 10px;
  margin-bottom: 10px;
}

button {
  width: 100%;
  padding: 10px;
  margin-bottom: 10px;
  cursor: pointer;
}

.social-login {
  margin-top: 20px;
}
</style>