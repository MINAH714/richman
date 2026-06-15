<!-- frontend/src/views/ChatPageView.vue -->
<template>
  <div class="chat-page">

    <!-- ── 헤더 ───────────────────────────────────────────── -->
    <div class="page-header">
      <h1>🤖 Richman AI 어시스턴트</h1>
      <p class="page-subtitle">암호화폐 · 주식 · 소비 통합 금융 어시스턴트</p>
      <button class="reset-btn" @click="resetChat">🔄 대화 초기화</button>
    </div>

    <!-- ── 비로그인 안내 ───────────────────────────────────── -->
    <div v-if="!authStore.isLoggedIn" class="login-required">
      <p>💬 챗봇 기능은 로그인 후 이용할 수 있어요!</p>
      <router-link to="/login" class="login-btn">로그인하러 가기</router-link>
    </div>

    <div v-else class="chat-layout">

      <!-- ── 채팅 영역 ─────────────────────────────────────── -->
      <div class="chat-main">

        <!-- 메시지 목록 -->
        <div class="chat-messages" ref="messagesEl">

          <!-- 웰컴 -->
          <div v-if="chatStore.messages.length === 0" class="welcome-section">
            <div class="welcome-icon">🤖</div>
            <h2>안녕하세요!</h2>
            <p>무엇이든 물어보세요. 실시간 데이터를 기반으로 답변해드릴게요.</p>

            <div class="quick-grid">
              <button
                v-for="q in quickQuestions"
                :key="q.text"
                class="quick-card"
                @click="quickSend(q.text)"
              >
                <span class="quick-icon">{{ q.icon }}</span>
                <span class="quick-text">{{ q.text }}</span>
              </button>
            </div>
          </div>

          <!-- 메시지들 -->
          <div
            v-for="msg in chatStore.messages"
            :key="msg.id"
            class="msg-wrapper"
            :class="msg.role"
          >
            <!-- 어시스턴트 아바타 -->
            <div v-if="msg.role === 'assistant'" class="msg-avatar">🤖</div>

            <div class="msg-bubble" :class="msg.role">
              <pre class="msg-content">{{ msg.content }}</pre>
              <div class="msg-meta">
                <span class="msg-time">{{ formatTime(msg.created_at) }}</span>
                <span v-if="msg.intent_type" class="intent-tag" :class="msg.intent_type">
                  {{ intentLabel(msg.intent_type) }}
                </span>
              </div>
            </div>
          </div>

          <!-- 로딩 -->
          <div v-if="chatStore.isLoading" class="msg-wrapper assistant">
            <div class="msg-avatar">🤖</div>
            <div class="msg-bubble assistant loading-bubble">
              <span class="dot" /><span class="dot" /><span class="dot" />
            </div>
          </div>
        </div>

        <!-- 입력창 -->
        <div class="chat-input-area">
          <textarea
            v-model="inputText"
            class="chat-input"
            placeholder="메시지를 입력하세요... (Enter: 전송 / Shift+Enter: 줄바꿈)"
            @keydown.enter.prevent="handleEnter"
            @input="autoResize"
            ref="inputEl"
            rows="1"
          />
          <button
            class="send-btn"
            @click="handleSend"
            :disabled="!inputText.trim() || chatStore.isLoading"
          >
            전송 ➤
          </button>
        </div>
      </div>

      <!-- ── 사이드 패널 ─────────────────────────────────── -->
      <aside class="chat-sidebar">
        <div class="sidebar-section">
          <h3>💡 추천 질문</h3>
          <div class="suggest-list">
            <button
              v-for="q in quickQuestions"
              :key="q.text"
              class="suggest-btn"
              @click="quickSend(q.text)"
            >
              {{ q.icon }} {{ q.text }}
            </button>
          </div>
        </div>

        <div class="sidebar-section">
          <h3>📌 사용 가이드</h3>
          <ul class="guide-list">
            <li>₿ <strong>코인 시세</strong>: "비트코인 얼마야?"</li>
            <li>🔔 <strong>가격 알림</strong>: "BTC 1억 되면 알려줘"</li>
            <li>📈 <strong>주식 조회</strong>: "삼성전자 주가 어때?"</li>
            <li>💸 <strong>소비 분석</strong>: "이번달 식비 얼마야?"</li>
          </ul>
        </div>
      </aside>

    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useAuthStore } from '@/stores/auth'

const chatStore = useChatStore()
const authStore = useAuthStore()

const inputText = ref('')
const messagesEl = ref(null)
const inputEl = ref(null)

const quickQuestions = [
  { icon: '₿', text: '비트코인 지금 얼마야?' },
  { icon: 'Ξ', text: '이더리움 시세 알려줘' },
  { icon: '🔔', text: '비트코인 1억 되면 알려줘' },
  { icon: '📈', text: '삼성전자 주가 어때?' },
  { icon: '💸', text: '이번달 소비 현황 알려줘' },
  { icon: '🔥', text: '요즘 핫한 코인 뭐야?' },
]

onMounted(async () => {
  if (authStore.isLoggedIn && !chatStore.sessionId) {
    await chatStore.initSession()
  }
})

async function handleSend() {
  const content = inputText.value.trim()
  if (!content || chatStore.isLoading) return
  inputText.value = ''
  resetInputHeight()
  await chatStore.sendMessage(content)
  scrollToBottom()
}

function handleEnter(e) {
  if (e.shiftKey) return
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
  el.style.height = Math.min(el.scrollHeight, 160) + 'px'
}

function resetInputHeight() {
  if (inputEl.value) inputEl.value.style.height = 'auto'
}

function formatTime(isoString) {
  if (!isoString) return ''
  return new Date(isoString).toLocaleTimeString('ko-KR', {
    hour: '2-digit', minute: '2-digit',
  })
}

function intentLabel(intent) {
  const map = {
    crypto: '₿ 크립토',
    stock: '📈 주식',
    consumption: '💸 소비',
    price_alert: '🔔 알림',
    mixed: '💬 일반',
  }
  return map[intent] ?? intent
}

watch(() => chatStore.messages.length, scrollToBottom)
</script>

<style scoped>
.chat-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 1.5rem;
  font-family: 'IBM Plex Mono', monospace;
  min-height: calc(100vh - 56px);
}

/* 헤더 */
.page-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.page-header h1 { margin: 0; font-size: 1.3rem; }
.page-subtitle { color: #6b7280; font-size: 0.8rem; flex: 1; margin: 0; }
.reset-btn {
  padding: 6px 14px;
  border: 1px solid #e2ecf9;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-size: 0.8rem;
  font-family: 'IBM Plex Mono', monospace;
}
.reset-btn:hover { background: #f0f6ff; }

/* 비로그인 */
.login-required {
  text-align: center;
  padding: 4rem;
  color: #6b7280;
}
.login-btn {
  display: inline-block;
  margin-top: 1rem;
  padding: 8px 20px;
  background: #6366f1;
  color: white;
  border-radius: 8px;
  text-decoration: none;
  font-size: 0.9rem;
}

/* 레이아웃 */
.chat-layout {
  display: grid;
  grid-template-columns: 1fr 260px;
  gap: 1.5rem;
  height: calc(100vh - 160px);
}

/* 채팅 메인 */
.chat-main {
  display: flex;
  flex-direction: column;
  background: white;
  border: 1px solid #e2ecf9;
  border-radius: 12px;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: #f8faff;
}

/* 웰컴 */
.welcome-section {
  text-align: center;
  padding: 2rem 1rem;
  color: #374151;
}
.welcome-icon { font-size: 3rem; margin-bottom: 0.5rem; }
.welcome-section h2 { font-size: 1.2rem; margin: 0 0 0.5rem; }
.welcome-section p { color: #6b7280; font-size: 0.85rem; margin-bottom: 1.5rem; }

.quick-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
  max-width: 480px;
  margin: 0 auto;
}
.quick-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 8px;
  background: white;
  border: 1px solid #e2ecf9;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.78rem;
  font-family: 'IBM Plex Mono', monospace;
  transition: all 0.15s;
  color: #374151;
}
.quick-card:hover { background: #6366f1; color: white; border-color: #6366f1; }
.quick-icon { font-size: 1.1rem; }

/* 메시지 */
.msg-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 8px;
}
.msg-wrapper.user { justify-content: flex-end; }
.msg-wrapper.assistant { justify-content: flex-start; }

.msg-avatar { font-size: 1.3rem; flex-shrink: 0; }

.msg-bubble {
  max-width: 70%;
  padding: 10px 14px;
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
  border: 1px solid #e2ecf9;
  color: #0f172a;
  border-bottom-left-radius: 4px;
}

.msg-content {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: 'IBM Plex Mono', monospace;
  line-height: 1.6;
}

.msg-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
}
.msg-time { font-size: 0.65rem; opacity: 0.5; }

.intent-tag {
  font-size: 0.65rem;
  padding: 1px 6px;
  border-radius: 10px;
  font-weight: 600;
}
.intent-tag.crypto { background: #fef3c7; color: #d97706; }
.intent-tag.stock { background: #dcfce7; color: #16a34a; }
.intent-tag.consumption { background: #fce7f3; color: #db2777; }
.intent-tag.price_alert { background: #ede9fe; color: #7c3aed; }
.intent-tag.mixed { background: #f1f5f9; color: #64748b; }

/* 로딩 */
.loading-bubble {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 14px 18px;
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
  padding: 10px 14px;
  font-size: 0.85rem;
  font-family: 'IBM Plex Mono', monospace;
  resize: none;
  outline: none;
  line-height: 1.5;
  max-height: 160px;
}
.chat-input:focus { border-color: #6366f1; }
.send-btn {
  padding: 10px 16px;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.85rem;
  font-family: 'IBM Plex Mono', monospace;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s;
}
.send-btn:hover:not(:disabled) { background: #4f46e5; }
.send-btn:disabled { background: #d1d5db; cursor: not-allowed; }

/* 사이드바 */
.chat-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.sidebar-section {
  background: white;
  border: 1px solid #e2ecf9;
  border-radius: 12px;
  padding: 1rem;
}
.sidebar-section h3 {
  font-size: 0.85rem;
  font-weight: 600;
  margin: 0 0 0.75rem;
  color: #374151;
}
.suggest-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.suggest-btn {
  text-align: left;
  padding: 6px 10px;
  background: #f8faff;
  border: 1px solid #e2ecf9;
  border-radius: 6px;
  font-size: 0.78rem;
  font-family: 'IBM Plex Mono', monospace;
  cursor: pointer;
  color: #374151;
  transition: all 0.15s;
}
.suggest-btn:hover { background: #6366f1; color: white; border-color: #6366f1; }

.guide-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 0.78rem;
  color: #6b7280;
  line-height: 1.5;
}
.guide-list li strong { color: #374151; }
</style>