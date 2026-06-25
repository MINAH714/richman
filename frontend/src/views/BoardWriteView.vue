<!-- src/views/BoardWriteView.vue -->
<template>
  <div class="write-page">
    <h2>{{ isEdit ? '게시글 수정' : '게시글 작성' }}</h2>

    <div class="form-group">
      <label>분류</label>
      <select v-model="form.category">
        <option v-for="cat in POST_CATEGORIES" :key="cat.value" :value="cat.value">
          {{ cat.label }}
        </option>
      </select>
    </div>

    <div class="form-group">
      <label>제목</label>
      <input v-model="form.title" type="text" placeholder="제목을 입력하세요" />
    </div>

    <div class="form-group">
      <label>내용</label>
      <textarea v-model="form.content" rows="12" placeholder="내용을 입력하세요"></textarea>
    </div>

    <div class="form-actions">
      <button class="btn-cancel" @click="router.back()">취소</button>
      <button class="btn-submit" @click="handleSubmit" :disabled="!canSubmit">
        {{ isEdit ? '수정 완료' : '등록' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { createPost, updatePost, getPostDetail } from '@/api/board'
import { POST_CATEGORIES } from '@/data/postCategories'

const router = useRouter()
const route  = useRoute()

const isEdit = computed(() => !!route.params.id)

const form = ref({
  category: 'free',
  title: '',
  content: '',
})

onMounted(async () => {
  if (isEdit.value) {
    const { data } = await getPostDetail(route.params.id)
    form.value = {
      category: data.category,
      title: data.title,
      content: data.content,
    }
  }
})

const canSubmit = computed(() => form.value.title.trim() && form.value.content.trim())

async function handleSubmit() {
  if (!canSubmit.value) return

  if (isEdit.value) {
    await updatePost(route.params.id, form.value)
    router.push(`/board/${route.params.id}`)
  } else {
    const { data } = await createPost(form.value)
    router.push(`/board/${data.id}`)
  }
}
</script>

<style scoped>
.write-page { max-width: 700px; margin: 0 auto; padding: 24px; font-family: var(--font-main, sans-serif); }
.write-page h2 { font-size: 1.2rem; font-weight: 700; margin-bottom: 20px; color: #1e293b; }

.form-group { margin-bottom: 16px; display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 0.82rem; font-weight: 600; color: #64748b; }
.form-group select,
.form-group input,
.form-group textarea {
  padding: 10px 12px; border: 1px solid #e2e8f0; border-radius: 8px;
  font-size: 0.9rem; font-family: inherit; color: #1e293b;
}
.form-group select { max-width: 220px; }
.form-group textarea { resize: vertical; line-height: 1.6; }

.form-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 8px; }
.btn-cancel, .btn-submit {
  padding: 9px 20px; border-radius: 8px; font-size: 0.85rem; font-weight: 600; cursor: pointer; border: none;
}
.btn-cancel { background: #f1f5f9; color: #64748b; }
.btn-submit { background: #3b6fd4; color: white; }
.btn-submit:disabled { background: #cbd5e1; cursor: not-allowed; }
</style>