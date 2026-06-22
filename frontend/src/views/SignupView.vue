<template>
  <div class="login-page">
    <div class="bg-blob bg-blob-1" aria-hidden="true"></div>
    <div class="bg-blob bg-blob-2" aria-hidden="true"></div>

    <div class="login-card">
      <div class="logo-wrap">
        <div class="logo-icon">◈</div>
        <h1 class="logo-text">회원가입</h1>
        <p class="logo-sub">Richman의 새로운 멤버가 되어보세요</p>
      </div>

      <transition name="slide-down">
        <div v-if="errorMsg" class="error-banner" role="alert">
          {{ errorMsg }}
        </div>
      </transition>

      <form @submit.prevent="handleSignup" class="login-form">
        <div class="field-wrap">
          <label class="field-label">아이디</label>
          <div class="input-wrap">
            <input v-model="form.username" type="text" class="field-input" placeholder="사용할 아이디" required :disabled="isLoading" />
          </div>
        </div>

        <div class="field-wr   ap">
          <label class="field-label">닉네임</label>
          <div class="input-wrap">
            <input v-model="form.nickname" type="text" class="field-input" placeholder="닉네임" required :disabled="isLoading" />
          </div>
        </div>

        <div class="field-wrap">
          <label class="field-label">비밀번호</label>
          <div class="input-wrap">
            <input v-model="form.password" type="password" class="field-input" placeholder="비밀번호" required :disabled="isLoading" />
          </div>
        </div>

        <div class="field-wrap">
          <label class="field-label">비밀번호 확인</label>
          <div class="input-wrap">
            <input v-model="form.passwordConfirm" type="password" class="field-input" placeholder="비밀번호 재입력" required :disabled="isLoading" />
          </div>
        </div>

        <button type="submit" class="btn-primary" :disabled="isLoading">
          {{ isLoading ? '가입 처리 중...' : '회원가입' }}
        </button>
      </form>

      <p class="signup-link">
        이미 계정이 있으신가요?
        <RouterLink to="/login">로그인</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/api/axios'

const router = useRouter()
const form = ref({ username: '', nickname: '', password: '', passwordConfirm: '' })
const isLoading = ref(false)
const errorMsg = ref('')

async function handleSignup() {
  if (form.value.password !== form.value.passwordConfirm) {
    errorMsg.value = '비밀번호가 일치하지 않습니다.'
    return
  }
  
  isLoading.value = true
  errorMsg.value = ''
  
  try {
    await axios.post('/api/accounts/signup/', {
      username: form.value.username,
      nickname: form.value.nickname,
      password: form.value.password
    })
    alert('가입이 완료되었습니다! 로그인 페이지로 이동합니다.')
    router.push('/login')
  } catch (err) {
    errorMsg.value = err.response?.data?.username ? '이미 존재하는 아이디입니다.' : '가입에 실패했습니다.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* 로그인 페이지의 스타일을 그대로 재사용합니다 */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600&display=swap');

.login-page {
  min-height: 100vh;
  background: linear-gradient(150deg, #eff6ff 0%, #f0f9ff 55%, #eef2ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  position: relative;
  overflow: hidden;
  font-family: 'Noto Sans KR', sans-serif;
}

.bg-blob { position: absolute; border-radius: 50%; pointer-events: none; z-index: 0; }
.bg-blob-1 { width: 500px; height: 500px; background: radial-gradient(circle, rgba(59,130,246,0.10) 0%, transparent 70%); top: -150px; right: -100px; }
.bg-blob-2 { width: 380px; height: 380px; background: radial-gradient(circle, rgba(99,102,241,0.09) 0%, transparent 70%); bottom: -100px; left: -80px; }

.login-card {
  position: relative; z-index: 1; width: 100%; max-width: 420px; background: #ffffff;
  border-radius: 20px; border: 1px solid #dbeafe;
  box-shadow: 0 12px 40px rgba(37,99,235,0.09);
  padding: 44px 40px; display: flex; flex-direction: column; gap: 24px;
}

.logo-wrap { text-align: center; }
.logo-icon { display: inline-flex; align-items: center; justify-content: center; width: 52px; height: 52px; background: #eff6ff; border: 1.5px solid #bfdbfe; border-radius: 14px; font-size: 22px; color: #2563eb; margin-bottom: 14px; }
.logo-text { margin: 0 0 4px; font-size: 20px; font-weight: 600; color: #0f172a; }
.logo-sub { margin: 0; font-size: 12px; color: #94a3b8; }

.login-form { display: flex; flex-direction: column; gap: 16px; }
.field-wrap { display: flex; flex-direction: column; gap: 6px; }
.field-label { font-size: 13px; font-weight: 500; color: #334155; }
.field-input { width: 100%; box-sizing: border-box; background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 10px; padding: 11px 12px; font-size: 14px; outline: none; }
.field-input:focus { border-color: #3b82f6; background: #fff; }

.error-banner { background: #fef2f2; border: 1px solid #fecaca; color: #dc2626; font-size: 13px; padding: 11px 14px; border-radius: 10px; }

.btn-primary { width: 100%; padding: 12px; background: #2563eb; border: none; color: #fff; font-weight: 600; cursor: pointer; border-radius: 10px; margin-top: 8px; }
.btn-primary:disabled { opacity: 0.5; }

.signup-link { text-align: center; font-size: 13px; color: #94a3b8; margin: 0; }
.signup-link a { color: #2563eb; font-weight: 500; text-decoration: none; margin-left: 4px; }
</style>