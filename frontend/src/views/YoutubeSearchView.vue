<template>
  <div class="youtube-page">

    <h1 class="page-title">
      📺 관심 종목 영상 자료
    </h1>

    <div class="search-box">
      <input
        v-model="keyword"
        class="search-input"
        placeholder="종목명을 입력하세요 (예: Apple, Tesla, 삼성전자)"
        @keyup.enter="search"
      >

      <button class="search-btn" @click="search">
        검색
      </button>
    </div>

    <h2 class="section-title">
      추천 영상
    </h2>

    <div class="video-list">

      <VideoCard
        v-for="video in videos"
        :key="video.id.videoId"
        :video="video"
      />

    </div>

    <p class="empty" v-if="searched && videos.length === 0">
      검색 결과가 없습니다.
    </p>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'   // ⭐ [신규 추가]
import { searchVideos } from '@/api/youtube'
import VideoCard from '@/components/youtube/VideoCard.vue'

const route = useRoute()   // ⭐ [신규 추가]

const keyword = ref('')
const videos = ref([])
const searched = ref(false)

async function search() {
  if (!keyword.value) return
  const response = await searchVideos(keyword.value)
  videos.value = response.data.items
  searched.value = true
}

onMounted(() => {
  // ⭐ [신규 추가] 차트 페이지의 "관련영상 더보기"에서 넘어온 경우, 그 키워드로 바로 검색
  if (route.query.keyword) {
    keyword.value = route.query.keyword
    search()
  } else {
    loadRecommend()
  }
})

async function loadRecommend() {
  const response = await searchVideos('미국 주식')
  videos.value = response.data.items.slice(0,5)
}
</script>

.youtube-page{
  max-width:1200px;
  margin:auto;
  padding:40px 20px;
}

.page-title{
  font-size:2rem;
  font-weight:700;
  margin-bottom:30px;
}

.search-box{
  display:flex;
  gap:15px;
  margin-bottom:50px;
}

.search-input{
  flex:1;
  padding:15px;
  border:none;
  border-radius:15px;
  background:#f3f4f6;
  font-size:16px;
}

.search-input:focus{
  outline:none;
}

.search-btn{
  background: var(--color-primary);
  color: white;
  border: none;
  /* background:#42b883;
  color:white;
  border:none; */
  border-radius:15px;
  padding:15px 30px;
  cursor:pointer;
  font-size:16px;
  font-weight:600;
}

.search-btn:hover{
  background:#2659ac;
}

.section-title{
  font-size:1.3rem;
  margin-bottom:20px;
}

.video-list{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(320px,1fr));
  gap:25px;
}

.empty{
  text-align:center;
  margin-top:50px;
  color:gray;
}

</style>