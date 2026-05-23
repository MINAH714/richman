<script setup>
import { useRoute, useRouter } from 'vue-router'
import axios from '@/api/axios'

const route = useRoute()
const router = useRouter()

const code = route.query.code

const googleLogin = async () => {
  try {
    const response = await axios.post('/api/accounts/google/login/', {
  code,
})

    console.log(response.data)

    localStorage.setItem(
      'access',
      response.data.access
    )

    localStorage.setItem(
      'refresh',
      response.data.refresh
    )

    router.push('/')
  } catch (error) {
    console.error(error)
  }
}

googleLogin()
</script>

<template>
  <div>
    Google 로그인 처리중...
  </div>
</template>