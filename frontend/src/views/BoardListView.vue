<!-- src/views/BoardListView.vue -->
<template>
  <div class="board-page">
    <div class="board-header">
      <h2>게시판</h2>
      <router-link to="/board/write" class="btn-write">✏️ 글쓰기</router-link>
    </div>

    <div class="category-tabs">
      <button
        class="tab"
        :class="{ active: selectedCategory === '' }"
        @click="selectCategory('')"
      >
        전체
      </button>
      <button
        v-for="cat in POST_CATEGORIES"
        :key="cat.value"
        class="tab"
        :class="{ active: selectedCategory === cat.value }"
        @click="selectCategory(cat.value)"
      >
        {{ cat.label }}
      </button>
    </div>

    <table class="post-table">
      <thead>
        <tr>
          <th class="col-category">분류</th>
          <th class="col-title">제목</th>
          <th class="col-author">작성자</th>
          <th class="col-date">작성일</th>
          <th class="col-views">조회</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading">
          <td colspan="5" class="status-cell">불러오는 중...</td>
        </tr>
        <tr v-else-if="posts.length === 0">
          <td colspan="5" class="status-cell">게시글이 없습니다.</td>
        </tr>
        <tr
          v-else
          v-for="post in posts"
          :key="post.id"
          class="post-row"
          @click="goDetail(post.id)"
        >
          <td class="col-category">
            <span class="category-badge" :class="`cat-${post.category}`">
              {{ post.category_display }}
            </span>
          </td>
          <td class="col-title">
            {{ post.title }}
            <span v-if="post.comment_count > 0" class="comment-count">[{{ post.comment_count }}]</span>
          </td>
          <td class="col-author">{{ post.author_name }}</td>
          <td class="col-date">{{ formatDate(post.created_at) }}</td>
          <td class="col-views">{{ post.view_count }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getPosts } from '@/api/board'
import { POST_CATEGORIES } from '@/data/postCategories'

const router = useRouter()
const posts = ref([])
const loading = ref(false)
const selectedCategory = ref('')

const fetchPosts = async () => {
  loading.value = true
  try {
    const { data } = await getPosts(selectedCategory.value)
    posts.value = data
  } finally {
    loading.value = false
  }
}

onMounted(fetchPosts)

const selectCategory = (cat) => {
  selectedCategory.value = cat
  fetchPosts()
}

const goDetail = (id) => router.push(`/board/${id}`)

const formatDate = (iso) => {
  const d = new Date(iso)
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`
}
</script>

<style scoped>
.board-page { max-width: 900px; margin: 0 auto; padding: 24px; font-family: var(--font-main, sans-serif); }
.board-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.board-header h2 { font-size: 1.3rem; font-weight: 700; color: #1e293b; }
.btn-write {
  background: #3b6fd4; color: white; padding: 8px 16px; border-radius: 8px;
  text-decoration: none; font-size: 0.85rem; font-weight: 600;
}

.category-tabs { display: flex; gap: 6px; margin-bottom: 16px; }
.tab {
  padding: 7px 14px; border: 1px solid #e2e8f0; border-radius: 20px;
  background: white; font-size: 0.82rem; color: #64748b; cursor: pointer;
  transition: all .15s;
}
.tab.active { background: #3b6fd4; color: white; border-color: #3b6fd4; }
.tab:hover:not(.active) { background: #f1f5f9; }

.post-table { width: 100%; border-collapse: collapse; }
.post-table thead th {
  text-align: left; font-size: 0.78rem; color: #94a3b8; font-weight: 600;
  padding: 10px 12px; border-bottom: 2px solid #e2e8f0;
}
.col-category { width: 100px; }
.col-author { width: 90px; }
.col-date   { width: 100px; }
.col-views  { width: 60px; text-align: center; }

.post-row { cursor: pointer; transition: background .15s; }
.post-row:hover { background: #f8faff; }
.post-row td {
  padding: 12px; border-bottom: 1px solid #f1f5f9; font-size: 0.85rem; color: #334155;
}
.col-views { text-align: center; color: #94a3b8; }
.comment-count { color: #3b6fd4; font-size: 0.78rem; margin-left: 4px; }

.category-badge {
  font-size: 0.72rem; padding: 3px 8px; border-radius: 6px; font-weight: 600;
  white-space: nowrap;
}
.cat-free   { background: #f1f5f9; color: #64748b; }
.cat-review { background: #eef2ff; color: #4f46e5; }
.cat-flex   { background: #fef3c7; color: #d97706; }
.cat-qna    { background: #dcfce7; color: #16a34a; }

.status-cell { text-align: center; padding: 3rem; color: #94a3b8; font-size: 0.85rem; }
</style>