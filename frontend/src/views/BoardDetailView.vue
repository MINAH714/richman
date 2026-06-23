<!-- src/views/BoardDetailView.vue -->
<template>
  <div class="detail-page" v-if="post">
    <div class="post-header">
      <span class="category-badge" :class="`cat-${post.category}`">{{ post.category_display }}</span>
      <h2>{{ post.title }}</h2>
      <div class="post-meta">
        <span>{{ post.author_name }}</span>
        <span>·</span>
        <span>{{ formatDate(post.created_at) }}</span>
        <span>·</span>
        <span>조회 {{ post.view_count }}</span>
      </div>
    </div>

    <div class="post-content">{{ post.content }}</div>

    <!-- 본인 글일 때만 수정/삭제 -->
    <div v-if="post.is_owner" class="post-actions">
      <button class="btn-edit" @click="router.push(`/board/${post.id}/edit`)">수정</button>
      <button class="btn-delete" @click="handleDeletePost">삭제</button>
    </div>

    <div class="comment-section">
      <h3>댓글 {{ post.comments.length }}개</h3>

      <ul class="comment-list">
        <li v-for="c in post.comments" :key="c.id" class="comment-item">
          <div v-if="editingCommentId !== c.id">
            <div class="comment-top">
              <span class="comment-author">{{ c.author_name }}</span>
              <span class="comment-date">{{ formatDate(c.created_at) }}</span>
            </div>
            <p class="comment-content">{{ c.content }}</p>

            <!-- 본인 댓글일 때만 수정/삭제 -->
            <div v-if="c.is_owner" class="comment-actions">
              <button @click="startEdit(c)">수정</button>
              <button @click="handleDeleteComment(c.id)">삭제</button>
            </div>
          </div>

          <!-- 댓글 수정 폼 -->
          <div v-else class="comment-edit-form">
            <textarea v-model="editingContent" rows="2"></textarea>
            <div class="comment-edit-actions">
              <button @click="confirmEdit(c.id)">완료</button>
              <button @click="cancelEdit">취소</button>
            </div>
          </div>
        </li>
        <li v-if="post.comments.length === 0" class="comment-empty">첫 댓글을 남겨보세요.</li>
      </ul>

      <div class="comment-write">
        <textarea v-model="newComment" rows="3" placeholder="댓글을 입력하세요"></textarea>
        <button @click="handleAddComment" :disabled="!newComment.trim()">댓글 등록</button>
      </div>
    </div>
  </div>

  <div v-else class="status-text">불러오는 중...</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getPostDetail, deletePost,
  createComment, updateComment, deleteComment,
} from '@/api/board'

const route  = useRoute()
const router = useRouter()

const post = ref(null)
const newComment = ref('')
const editingCommentId = ref(null)
const editingContent   = ref('')

const fetchPost = async () => {
  const { data } = await getPostDetail(route.params.id)
  post.value = data
}

onMounted(fetchPost)

async function handleDeletePost() {
  if (!confirm('게시글을 삭제하시겠습니까?')) return
  await deletePost(post.value.id)
  router.push('/board')
}

async function handleAddComment() {
  if (!newComment.value.trim()) return
  await createComment(post.value.id, newComment.value)
  newComment.value = ''
  await fetchPost()
}

function startEdit(comment) {
  editingCommentId.value = comment.id
  editingContent.value = comment.content
}

function cancelEdit() {
  editingCommentId.value = null
  editingContent.value = ''
}

async function confirmEdit(commentId) {
  if (!editingContent.value.trim()) return
  await updateComment(commentId, editingContent.value)
  cancelEdit()
  await fetchPost()
}

async function handleDeleteComment(commentId) {
  if (!confirm('댓글을 삭제하시겠습니까?')) return
  await deleteComment(commentId)
  await fetchPost()
}

const formatDate = (iso) => {
  const d = new Date(iso)
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}
</script>

<style scoped>
.detail-page { max-width: 700px; margin: 0 auto; padding: 24px; font-family: var(--font-main, sans-serif); }
.status-text { text-align: center; padding: 4rem; color: #94a3b8; }

.post-header { border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 16px; }
.post-header h2 { font-size: 1.25rem; font-weight: 700; color: #1e293b; margin: 8px 0; }
.post-meta { display: flex; gap: 6px; font-size: 0.8rem; color: #94a3b8; }

.category-badge { font-size: 0.72rem; padding: 3px 8px; border-radius: 6px; font-weight: 600; }
.cat-free   { background: #f1f5f9; color: #64748b; }
.cat-review { background: #eef2ff; color: #4f46e5; }
.cat-flex   { background: #fef3c7; color: #d97706; }
.cat-qna    { background: #dcfce7; color: #16a34a; }

.post-content { font-size: 0.92rem; line-height: 1.8; color: #334155; white-space: pre-wrap; min-height: 120px; margin-bottom: 16px; }

.post-actions { display: flex; justify-content: flex-end; gap: 8px; margin-bottom: 24px; }
.post-actions button {
  padding: 6px 14px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; cursor: pointer; border: none;
}
.btn-edit { background: #f1f5f9; color: #64748b; }
.btn-delete { background: #fef2f2; color: #ef4444; }

.comment-section { border-top: 1px solid #e2e8f0; padding-top: 20px; }
.comment-section h3 { font-size: 0.95rem; font-weight: 700; margin-bottom: 14px; color: #1e293b; }

.comment-list { list-style: none; padding: 0; margin: 0 0 20px; }
.comment-item { padding: 12px 0; border-bottom: 1px solid #f1f5f9; }
.comment-top { display: flex; gap: 8px; align-items: baseline; margin-bottom: 4px; }
.comment-author { font-size: 0.85rem; font-weight: 700; color: #334155; }
.comment-date { font-size: 0.74rem; color: #cbd5e1; }
.comment-content { font-size: 0.85rem; color: #475569; line-height: 1.6; margin: 0 0 6px; white-space: pre-wrap; }
.comment-actions { display: flex; gap: 8px; }
.comment-actions button {
  font-size: 0.74rem; background: none; border: none; color: #94a3b8; cursor: pointer; padding: 0;
}
.comment-actions button:hover { color: #3b6fd4; }
.comment-empty { text-align: center; padding: 2rem 0; color: #cbd5e1; font-size: 0.85rem; }

.comment-edit-form textarea {
  width: 100%; padding: 8px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 0.85rem; font-family: inherit; resize: vertical;
}
.comment-edit-actions { display: flex; gap: 6px; margin-top: 6px; }
.comment-edit-actions button {
  font-size: 0.78rem; padding: 4px 10px; border-radius: 6px; border: none; cursor: pointer;
}
.comment-edit-actions button:first-child { background: #3b6fd4; color: white; }
.comment-edit-actions button:last-child { background: #f1f5f9; color: #64748b; }

.comment-write { display: flex; flex-direction: column; gap: 8px; }
.comment-write textarea {
  width: 100%; padding: 10px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 0.85rem; font-family: inherit; resize: vertical;
}
.comment-write button {
  align-self: flex-end; padding: 7px 16px; background: #3b6fd4; color: white; border: none;
  border-radius: 8px; font-size: 0.82rem; font-weight: 600; cursor: pointer;
}
.comment-write button:disabled { background: #cbd5e1; cursor: not-allowed; }
</style>