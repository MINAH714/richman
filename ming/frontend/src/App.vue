<template>
  <div class="container">
    <h1>Richman 네이버 로그인 테스트</h1>
    <hr />

    <div v-if="!isLoggedIn">
      <p>로그인이 필요합니다.</p>
      <button @click="loginWithNaver" class="naver-btn">
        네이버로 로그인하기
      </button>
    </div>

    <div v-else class="result-box">
      <h3>🎉 로그인 성공!</h3>
      <p>장고로부터 받은 JWT 토큰:</p>
      <pre>{{ jwtToken }}</pre>
      <button @click="logout" class="logout-btn">로그아웃</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

// --- 설정값 (본인의 Client ID로 수정하세요) ---
const clientId = 'YOUR_NAVER_CLIENT_ID'; 
const callbackUrl = encodeURIComponent('http://localhost:5173');
const state = 'richman_test';

const isLoggedIn = ref(false);
const jwtToken = ref(null);

// 1. 네이버 로그인 페이지로 보내기
const loginWithNaver = () => {
  const naverUrl = `https://nid.naver.com/oauth2.0/authorize?response_type=token&client_id=${clientId}&redirect_uri=${callbackUrl}&state=${state}`;
  window.location.href = naverUrl;
};

// 2. 페이지가 켜질 때 URL에 토큰이 있는지 확인 (Callback 처리)
onMounted(() => {
  const hash = window.location.hash;
  if (hash) {
    const params = new URLSearchParams(hash.substring(1));
    const naverToken = params.get('access_token');

    if (naverToken) {
      sendToDjango(naverToken);
    }
  }
});

// 3. 장고 백엔드 API 호출
const sendToDjango = async (token) => {
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/naver/login/', {
      access_token: token
    });
    jwtToken.value = response.data;
    isLoggedIn.value = true;
    console.log('Django Login Success:', response.data);
  } catch (error) {
    console.error('Django Login Error:', error.response?.data || error.message);
    alert('장고 서버와 통신에 실패했습니다. (CORS 또는 서버 확인)');
  }
};

const logout = () => {
  isLoggedIn.value = false;
  jwtToken.value = null;
  window.location.href = '/';
};
</script>

<style scoped>
.container { text-align: center; margin-top: 50px; font-family: sans-serif; }
.naver-btn { background: #03C75A; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 5px; cursor: pointer; }
.logout-btn { background: #ff4444; color: white; border: none; padding: 8px 16px; margin-top: 20px; cursor: pointer; }
.result-box { background: #f9f9f9; padding: 20px; border: 1px solid #ddd; border-radius: 10px; display: inline-block; text-align: left; }
pre { white-space: pre-wrap; word-wrap: break-word; font-size: 12px; color: #333; }
</style>