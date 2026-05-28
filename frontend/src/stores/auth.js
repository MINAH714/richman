import { defineStore } from 'pinia'
import api from '@/api/axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    access: localStorage.getItem('access') || null,
    refresh: localStorage.getItem('refresh') || null,
  }),

  getters: {
    isLoggedIn: (state) => !!state.access,
  },

  actions: {
    async login(username, password) {
      const res = await api.post('/api/token/', {
        username,
        password,
      })

      this.access = res.data.access
      this.refresh = res.data.refresh

      localStorage.setItem('access', res.data.access)
      localStorage.setItem('refresh', res.data.refresh)
    },

    setTokens(access, refresh) {
      this.access = access
      this.refresh = refresh

      localStorage.setItem('access', access)
      localStorage.setItem('refresh', refresh)
    },

    logout() {
      this.access = null
      this.refresh = null

      localStorage.removeItem('access')
      localStorage.removeItem('refresh')

      window.location.href = '/login'
    },
  },
})