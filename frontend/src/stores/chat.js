// frontend/src/stores/chat.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { chatAPI } from '@/api/chat'

export const useChatStore = defineStore('chat', () => {
  const sessionId = ref(null)
  const messages = ref([])
  const isLoading = ref(false)

  async function initSession() {
    try {
      const { data } = await chatAPI.createSession()
      sessionId.value = data.id
      messages.value = []
    } catch (e) {
      console.error('[chat] 세션 생성 실패:', e)
    }
  }

  async function sendMessage(content) {
    if (!sessionId.value) await initSession()

    // 사용자 메시지 즉시 표시
    messages.value.push({
      id: Date.now(),
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    })

    isLoading.value = true
    try {
      const { data } = await chatAPI.sendMessage(sessionId.value, content)
      messages.value.push(data.message)
      return data
    } catch (e) {
      messages.value.push({
        id: Date.now(),
        role: 'assistant',
        content: '죄송해요, 일시적인 오류가 발생했어요. 다시 시도해주세요.',
        created_at: new Date().toISOString(),
      })
    } finally {
      isLoading.value = false
    }
  }

  function clearMessages() {
    messages.value = []
    sessionId.value = null
  }

  return {
    sessionId,
    messages,
    isLoading,
    initSession,
    sendMessage,
    clearMessages,
  }
})