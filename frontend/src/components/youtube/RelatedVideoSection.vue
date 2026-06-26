<template>
  <section class="related-video-section">
    <div class="related-header">
      <h3 class="related-title">📺 관련 영상</h3>
      <button class="more-btn" @click="goToFullSearch">
        관련영상 더보기 →
      </button>
    </div>

    <div v-if="isLoading" class="related-loading">영상을 불러오는 중...</div>

    <div v-else-if="videos.length > 0" class="related-video-row">
      <VideoCard
        v-for="video in videos"
        :key="video.id.videoId"
        :video="video"
      />
    </div>

    <p v-else class="related-empty">관련 영상을 찾을 수 없습니다.</p>
  </section>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { searchVideos } from '@/api/youtube'
import VideoCard from '@/components/youtube/VideoCard.vue'

const props = defineProps({
  keyword: { type: String, required: true },   // 검색 키워드 (예: "삼성전자 주식")
})

const router    = useRouter()
const videos    = ref([])
const isLoading = ref(false)

async function loadVideos() {
  if (!props.keyword) return
  isLoading.value = true
  videos.value = []
  try {
    const response = await searchVideos(props.keyword)
    const items = response.data.items
    videos.value = items ? items.slice(0, 4) : []   // ⭐ 4개만 표시
  } catch (err) {
    console.warn('관련 영상 로드 실패:', err)
    videos.value = []
  } finally {
    isLoading.value = false
  }
}

// 더보기 버튼 → 같은 키워드로 /youtube 페이지로 이동해서 이어서 검색
function goToFullSearch() {
  router.push({ name: 'youtube-search', query: { keyword: props.keyword } })
}

onMounted(loadVideos)
watch(() => props.keyword, loadVideos)
</script>

<style scoped>
.related-video-section {
  margin-top: 24px;
  padding-top: 20px;
}
.related-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.related-title {
  font-size: 1rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}
.more-btn {
  padding: 5px 12px;
  border: 1px solid #d0e2f5;
  border-radius: 99px;
  background: #fff;
  color: #2563eb;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s;
}
.more-btn:hover {
  background: #2563eb;
  color: #fff;
}

/* ⭐ [신규] 4개 카드를 한 줄에 배치 */
.related-video-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.related-loading,
.related-empty {
  color: #94a3b8;
  font-size: 0.85rem;
  padding: 20px 0;
}

/* 화면이 좁아지면 2열로 줄여서 카드가 너무 찌그러지지 않게 */
@media (max-width: 900px) {
  .related-video-row {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>