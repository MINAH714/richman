<!-- src/components/mypage/ProfileTab.vue -->
<template>
  <div class="profile-card">
    <div class="profile-avatar">{{ initial }}</div>
    <p class="profile-name">{{ authStore.user?.nickname || authStore.user?.username || '...' }}</p>
    <p class="profile-email">{{ authStore.user?.email }}</p>

    <div class="profile-divider" />

    <ul class="profile-meta">
      <li>
        <span class="meta-label">ID</span>
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
  background: #ffffff;
  border: 1px solid #e1e3e4;
  padding: 32px 24px;
  text-align: center;
  position: sticky;
  top: 80px;
  font-family: 'Inter', sans-serif;
  border-radius: 0;
}
.profile-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #191c1d;
  color: #ffffff;
  font-family: 'Hanken Grotesk', sans-serif;
  font-size: 1.3rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}
.profile-name {
  font-family: 'Hanken Grotesk', sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
  margin: 0 0 4px;
  color: #191c1d;
}
.profile-email {
  font-size: .78rem;
  color: #4c4546;
  margin: 0;
}
.profile-divider {
  height: 1px;
  background: #e1e3e4;
  margin: 22px 0;
}
.profile-meta {
  list-style: none;
  padding: 0;
  margin: 0 0 22px;
  text-align: left;
}
.profile-meta li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: .8rem;
  padding: 8px 0;
}
.meta-label {
  font-family: 'Geist', sans-serif;
  letter-spacing: 0.05em;
  font-size: 11px;
  color: #4c4546;
  text-transform: uppercase;
}
.meta-value { color: #191c1d; font-weight: 600; }
.profile-logout {
  width: 100%;
  padding: 10px;
  border: 1px solid #191c1d;
  background: #ffffff;
  color: #191c1d;
  font-size: .8rem;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  transition: background .12s, color .12s;
  border-radius: 0;
}
.profile-logout:hover { background: #191c1d; color: #ffffff; }
</style>