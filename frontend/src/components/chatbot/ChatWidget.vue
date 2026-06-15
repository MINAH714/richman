<!-- frontend/src/components/chatbot/ChatWidget.vue -->
<template>
  <div class="chat-widget">

    <!-- ── 플로팅 버튼 ─────────────────────────────────── -->
    <button
      class="chat-toggle-btn"
      @click="toggleChat"
      :class="{ open: isOpen }"
    >
      <span v-if="!isOpen">💬</span>
      <span v-else>✕</span>
    </button>

    <!-- ── 채팅창 ──────────────────────────────────────── -->
    <transition name="chat-slide">
      <div v-if="isOpen" class="chat-window">

        <!-- 헤더 -->
        <div class="chat-header">
          <div class="chat-header-info">
            <span class="chat-avatar">🤖</span>
            <div>
              <div class="chat-title">Richman AI</div>
              <div class="chat-subtitle">crypto · stock · 소비 통합 어시스턴트</div>
            </div>
          </div>
          <button class="chat-reset-btn" @click="resetChat" title="대화 초기화">🔄</button>
        </div>

        <!-- 메시지 목록 -->
        <div class="chat-messages" ref="messagesEl">
          <!-- 웰컴 메시지 -->
          <div v-if="chatStore.messages.length === 0" class="welcome-msg">
            <p>안녕하세요! 💰</p>
            <p>저는 Richman AI 어시스턴트예요.</p>
            <div class="quick-btns">
              <button @click="quickSend('비트코인 지금 얼마야?')">₿ BTC 시세</button>
              <button @click="quickSend('이더리움 알려줘')">Ξ ETH 시세</button>
              <button @click="quickSend('이번달 소비 어때?')">💸 소비 현황</button>
              <button @click="quickSend('삼성전자 주가 어때?')">📈 주식 시세</button>
            </div>
          </div>

          <!-- 메시지들 -->
          <div
            v-for="msg in chatStore.messages"
            :key="msg.id"
            class="msg-wrapper"
            :class="msg.role"
          >
            <div class="msg-bubble" :class="msg.role">
              <pre class="msg-content">{{ msg.content }}</pre>
              <div class="msg-time">
                {{ formatTime(msg.created_at) }}
                <span v-if="msg.intent_type" class="intent-badge">{{ intentLabel(msg.intent_type) }}</span>
              </div>
            </div>
          </div>

          <!-- 로딩 -->
          <div v-if="chatStore.isLoading" class="msg-wrapper assistant">
            <div class="msg-bubble assistant loading">
              <span class="dot" /><span class="dot" /><span class="dot" />
            </div>
          </div>
        </div>

        <!-- 입력창 -->
        <div class="chat-input-area">
          <textarea
            v-model="inputText"
            class="chat-input"
            placeholder="메시지를 입력하세요..."
            rows="1"
            @keydown.enter.prevent="handleEnter"
            @input="autoResize"
            ref="inputEl"
          />
          <button
            class="chat-send-btn"
            @click="handleSend"
            :disabled="!inputText.trim() || chatStore.isLoading"
          >
            ➤
          </button>
        </div>

      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useAuthStore } from '@/stores/auth'

const chatStore = useChatStore()
const authStore = useAuthStore()

const isOpen = ref(false)
const inputText = ref('')
const messagesEl = ref(null)
const inputEl = ref(null)

function toggleChat() {
  isOpen.value = !isOpen.value
  if (isOpen.value && !chatStore.sessionId && authStore.isLoggedIn) {
    chatStore.initSession()
  }
}

async function handleSend() {
  const content = inputText.value.trim()
  if (!content || chatStore.isLoading) return

  if (!authStore.isLoggedIn) {
    chatStore.messages.push({
      id: Date.now(),
      role: 'assistant',
      content: '로그인 후 이용할 수 있어요! 로그인 페이지로 이동해주세요.',
      created_at: new Date().toISOString(),
    })
    return
  }

  inputText.value = ''
  resetInputHeight()
  await chatStore.sendMessage(content)
  scrollToBottom()
}

function handleEnter(e) {
  if (e.shiftKey) return  // Shift+Enter는 줄바꿈
  handleSend()
}

function quickSend(text) {
  inputText.value = text
  handleSend()
}

async function resetChat() {
  chatStore.clearMessages()
  await chatStore.initSession()
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesEl.value) {
      messagesEl.value.scrollTop = messagesEl.value.scrollHeight
    }
  })
}

function autoResize(e) {
  const el = e.target
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 120) + 'px'
}

function resetInputHeight() {
  if (inputEl.value) {
    inputEl.value.style.height = 'auto'
  }
}

function formatTime(isoString) {
  if (!isoString) return ''
  return new Date(isoString).toLocaleTimeString('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

function intentLabel(intent) {
  const map = {
    crypto: '₿',
    stock: '📈',
    consumption: '💸',
    price_alert: '🔔',
    mixed: '💬',
  }
  return map[intent] ?? ''
}

// 메시지 추가될 때마다 스크롤
watch(() => chatStore.messages.length, scrollToBottom)
</script>

<style scoped>
/* ── 플로팅 버튼 ───────────────────────────────────────── */
.chat-widget {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
}

.chat-toggle-btn {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #6366f1;
  border: none;
  cursor: pointer;
  font-size: 1.4rem;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4);
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.chat-toggle-btn:hover { background: #4f46e5; transform: scale(1.05); }
.chat-toggle-btn.open { background: #6b7280; }

/* ── 채팅창 ────────────────────────────────────────────── */
.chat-window {
  position: absolute;
  bottom: 68px;
  right: 0;
  width: 360px;
  height: 520px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: 'IBM Plex Mono', monospace;
}

/* 헤더 */
.chat-header {
  background: #6366f1;
  color: white;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.chat-header-info { display: flex; align-items: center; gap: 10px; }
.chat-avatar { font-size: 1.5rem; }
.chat-title { font-weight: 600; font-size: 0.95rem; }
.chat-subtitle { font-size: 0.7rem; opacity: 0.8; }
.chat-reset-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  opacity: 0.8;
}
.chat-reset-btn:hover { opacity: 1; }

/* 메시지 목록 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: #f8faff;
}

/* 웰컴 */
.welcome-msg {
  text-align: center;
  color: #6b7280;
  font-size: 0.85rem;
  padding: 1rem 0;
}
.welcome-msg p { margin: 4px 0; }
.quick-btns {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: center;
  margin-top: 12px;
}
.quick-btns button {
  padding: 4px 10px;
  background: white;
  border: 1px solid #e2ecf9;
  border-radius: 20px;
  font-size: 0.75rem;
  cursor: pointer;
  font-family: 'IBM Plex Mono', monospace;
  transition: all 0.15s;
}
.quick-btns button:hover { background: #6366f1; color: white; border-color: #6366f1; }

/* 메시지 버블 */
.msg-wrapper { display: flex; }
.msg-wrapper.user { justify-content: flex-end; }
.msg-wrapper.assistant { justify-content: flex-start; }

.msg-bubble {
  max-width: 80%;
  padding: 8px 12px;
  border-radius: 12px;
  font-size: 0.85rem;
}
.msg-bubble.user {
  background: #6366f1;
  color: white;
  border-bottom-right-radius: 4px;
}
.msg-bubble.assistant {
  background: white;
  color: #0f172a;
  border: 1px solid #e2ecf9;
  border-bottom-left-radius: 4px;
}

.msg-content {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.85rem;
  line-height: 1.5;
}

.msg-time {
  font-size: 0.65rem;
  opacity: 0.6;
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.msg-wrapper.user .msg-time { justify-content: flex-end; }

.intent-badge {
  font-size: 0.7rem;
  opacity: 0.8;
}

/* 로딩 점 */
.loading {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
}
.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #6366f1;
  animation: bounce 1.2s infinite;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-6px); }
}

/* 입력창 */
.chat-input-area {
  padding: 12px;
  border-top: 1px solid #e2ecf9;
  display: flex;
  gap: 8px;
  align-items: flex-end;
  background: white;
}
.chat-input {
  flex: 1;
  border: 1px solid #e2ecf9;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 0.85rem;
  font-family: 'IBM Plex Mono', monospace;
  resize: none;
  outline: none;
  line-height: 1.4;
  max-height: 120px;
  overflow-y: auto;
}
.chat-input:focus { border-color: #6366f1; }

.chat-send-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #6366f1;
  border: none;
  color: white;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.15s;
}
.chat-send-btn:hover:not(:disabled) { background: #4f46e5; }
.chat-send-btn:disabled { background: #d1d5db; cursor: not-allowed; }

/* 슬라이드 애니메이션 */
.chat-slide-enter-active,
.chat-slide-leave-active { transition: all 0.25s ease; }
.chat-slide-enter-from,
.chat-slide-leave-to {
  opacity: 0;
  transform: translateY(16px) scale(0.95);
}
</style>