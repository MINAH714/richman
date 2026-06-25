<template>
  <div class="video-card" @click="goDetail">
    <img :src="video.snippet.thumbnails.medium.url" />

    <div class="info">
      <h3>{{ video.snippet.title }}</h3>
      <p>{{ video.snippet.channelTitle }}</p>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  video: Object
})

const router = useRouter()

function goDetail() {
  router.push(`/youtube/${props.video.id.videoId}`)
}
</script>

<style scoped>
.video-card{
  cursor:pointer;
  border-radius:18px;
  overflow:hidden;
  background:white;
  box-shadow:0 4px 15px rgba(0,0,0,0.1);
  transition:.3s;
}

.video-card:hover{
  transform:translateY(-8px);
}

.video-card img{
  width:100%;
  height:200px;
  object-fit:cover;
}

.info{
  padding:15px;
}

.info h3{
  font-size:1rem;
  line-height:1.5;
  margin-bottom:10px;
}

.info p{
  color:#666;
}
</style>