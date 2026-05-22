<script setup>
import { onMounted } from 'vue'
import api from './api/axios'

onMounted(async () => {
  const res = await api.get('/api/accounts/test/')
  console.log(res.data)
})
</script>

<template>
  <div>
    Vue Django Connected
  </div>
</template>