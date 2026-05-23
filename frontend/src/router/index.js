import { createRouter, createWebHistory } from 'vue-router'

import LoginView from '@/views/LoginView.vue'
import HomeView from '@/views/HomeView.vue'
import GoogleCallbackView
from '@/views/oauth/GoogleCallbackView.vue'

const routes = [
  {
    path: '/login',
    component: LoginView,
  },
  {
    path: '/',
    component: HomeView,
    meta: { requiresAuth: true },
  },
  {
  path: '/oauth/google/callback',
  name: 'google-callback',
  component: GoogleCallbackView,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('access')

  if (to.meta.requiresAuth && !token) {
    return '/login'
  }
})

export default router