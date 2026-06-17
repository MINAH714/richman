<!-- src/components/mypage/ProfileTab.vue -->
<template>
  <div class="profile-card">
    <div class="profile-avatar">{{ initial }}</div>
    <p class="profile-name">{{ authStore.user?.nickname || authStore.user?.username || '...' }}</p>
    <p class="profile-email">{{ authStore.user?.email }}</p>
    <div class="profile-divider" />
    <ul class="profile-meta">
      <li>
        <span class="meta-label">아이디</span>
        <span class="meta-value">{{ authStore.user?.username }}</span>
      </li>
    </ul>
    <button class="profile-logout" @click="logout">로그아웃</button>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router    = useRouter()

onMounted(() => {
  if (!authStore.user) authStore.fetchProfile()
})

const initial = computed(() =>
  (authStore.user?.nickname || authStore.user?.username || '?')[0]
)

function logout() {
  authStore.logout()
  router.push('/')
}
</script>

<style scoped>
.profile-card {
  background: white; border: 1px solid #e2ecf9; border-radius: 12px;
  padding: 28px 20px; text-align: center; position: sticky; top: 80px;
  font-family: 'IBM Plex Mono', monospace;
}
.profile-avatar {
  width: 64px; height: 64px; border-radius: 50%; background: #3b6fd4;
  color: white; font-size: 1.6rem; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 14px;
}
.profile-name  { font-size: 1.05rem; font-weight: 700; margin: 0 0 4px; color: #0f172a; }
.profile-email { font-size: .78rem; color: #94a3b8; margin: 0; }
.profile-divider { height: 1px; background: #e2ecf9; margin: 18px 0; }
.profile-meta  { list-style: none; padding: 0; margin: 0 0 18px; text-align: left; }
.profile-meta li { display: flex; justify-content: space-between; font-size: .8rem; padding: 6px 0; }
.meta-label { color: #94a3b8; }
.meta-value { color: #374151; font-weight: 600; }
.profile-logout {
  width: 100%; padding: 9px; border-radius: 8px; border: 1px solid #d0e2f5;
  background: white; color: #64748b; font-size: .8rem; font-weight: 600;
  cursor: pointer; font-family: inherit; transition: all .15s;
}
.profile-logout:hover { background: #f1f5f9; }
</style>