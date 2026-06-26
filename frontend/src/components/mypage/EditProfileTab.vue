<!-- src/components/mypage/EditProfileTab.vue -->
<template>
  <div class="edit-tab">
    <section class="edit-section">
      <h3 class="section-title"><span class="section-eyebrow">PROFILE</span>프로필 수정</h3>

      <div class="form-row">
        <label>아이디</label>
        <input type="text" :value="authStore.user?.username" disabled />
      </div>

      <div class="form-row">
        <label>닉네임</label>
        <input type="text" v-model="form.nickname" placeholder="닉네임" />
      </div>

      <div class="form-row">
        <label>이메일</label>
        <input type="email" v-model="form.email" placeholder="email@example.com" />
      </div>

      <div class="form-actions">
        <span v-if="savedMessage" class="saved-message">{{ savedMessage }}</span>
        <button class="btn-save" @click="handleSave" :disabled="saving">
          {{ saving ? '저장 중...' : '저장' }}
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const form = ref({ nickname: '', email: '' })
const saving = ref(false)
const savedMessage = ref('')

onMounted(async () => {
  if (!authStore.user) await authStore.fetchProfile()
  syncForm()
})

watch(() => authStore.user, syncForm)

function syncForm() {
  form.value = {
    nickname: authStore.user?.nickname || '',
    email: authStore.user?.email || '',
  }
}

async function handleSave() {
  saving.value = true
  savedMessage.value = ''
  try {
    await authStore.updateProfile(form.value)
    savedMessage.value = '저장되었습니다'
    setTimeout(() => { savedMessage.value = '' }, 2500)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.edit-tab { font-family: 'Inter', sans-serif; }
.edit-section {
  background: #ffffff;
  border: 1px solid #e1e3e4;
  padding: 32px;
  max-width: 440px;
}
.section-title {
  font-family: 'Hanken Grotesk', sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
  margin: 0 0 24px;
  color: #191c1d;
  display: flex;
  align-items: baseline;
  gap: 10px;
}
.section-eyebrow {
  font-family: 'Geist', sans-serif;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.08em;
  color: #0050cc;
}

.form-row {
  margin-bottom: 18px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-row label {
  font-family: 'Geist', sans-serif;
  font-size: 11px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: #4c4546;
}
.form-row input {
  padding: 10px 12px;
  border: 1px solid #cfc4c5;
  border-radius: 0;
  font-size: .88rem;
  font-family: 'Inter', sans-serif;
  color: #191c1d;
}
.form-row input:focus {
  outline: none;
  border-color: #191c1d;
}
.form-row input:disabled {
  background: #f8f9fa;
  color: #9a9192;
}

.form-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}
.saved-message {
  font-size: .78rem;
  color: #0050cc;
  font-weight: 600;
}
.btn-save {
  padding: 10px 22px;
  border: 1px solid #191c1d;
  background: #191c1d;
  color: #ffffff;
  font-size: .85rem;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  transition: background .12s;
  border-radius: 0;
}
.btn-save:hover { background: #0050cc; border-color: #0050cc; }
.btn-save:disabled { background: #cfc4c5; border-color: #cfc4c5; cursor: not-allowed; }
</style>