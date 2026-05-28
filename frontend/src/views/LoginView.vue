<script setup>
import { ref } from 'vue'
import axios from '@/api/axios'

const username = ref('')
const password = ref('')

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

const googleLogin = () => {
  const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID
  const REDIRECT_URI = 'http://localhost:5173/oauth/google/callback'
  const scope = 'email profile'

  const googleURL =
    `https://accounts.google.com/o/oauth2/v2/auth` +
    `?client_id=${CLIENT_ID}` +
    `&redirect_uri=${REDIRECT_URI}` +
    `&response_type=code` +
    `&scope=${scope}`

  window.location.href = googleURL
}

const naverLogin = () => {
  const state = Math.random().toString(36).substring(2)
  const naverURL =
    `https://nid.naver.com/oauth2.0/authorize` +
    `?client_id=${import.meta.env.VITE_NAVER_CLIENT_ID}` +
    `&redirect_uri=${encodeURIComponent(import.meta.env.VITE_NAVER_REDIRECT_URI)}` +
    `&response_type=code` +
    `&state=${state}`

  window.location.href = naverURL
}
</script>

<template>
  <div class="login-container">
    <h1>로그인</h1>

    <form @submit.prevent="login">
      <div>
        <input v-model="username" type="text" placeholder="아이디" />
      </div>
      <div>
        <input v-model="password" type="password" placeholder="비밀번호" />
      </div>
      <button type="submit">로그인</button>
    </form>

    <hr />

    <div class="social-login">
      <button type="button" @click="googleLogin">Google 로그인</button>
      <button type="button" @click="kakaoLogin">Kakao 로그인</button>
      <button type="button" @click="naverLogin">Naver 로그인</button>
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