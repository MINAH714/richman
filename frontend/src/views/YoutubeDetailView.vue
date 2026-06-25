<template>

  <div class="container">

    <iframe
      width="100%"
      height="500"
      :src="youtubeUrl"
      frameborder="0"
      allowfullscreen
    />

    <h2>{{ title }}</h2>

    <p>채널 : {{ channel }}</p>

    <p>업로드 날짜 : {{ publishDate }}</p>

  </div>

</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()

const title = ref('')
const channel = ref('')
const publishDate = ref('')

const youtubeUrl = computed(() => {
  return `https://www.youtube.com/embed/${route.params.videoId}`
})

onMounted(async () => {

  const response = await axios.get(
    'https://www.googleapis.com/youtube/v3/videos',
    {
      params:{
        part:'snippet',
        id:route.params.videoId,
        key:import.meta.env.VITE_YOUTUBE_API_KEY
      }
    }
  )

  const item = response.data.items[0]

  title.value = item.snippet.title
  channel.value = item.snippet.channelTitle
  publishDate.value = item.snippet.publishedAt
})
</script>