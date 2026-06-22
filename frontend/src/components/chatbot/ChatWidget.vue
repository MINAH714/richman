<template>
  <div class="chat-widget">

    <button
      class="chat-toggle-btn"
      @click="toggleChat"
      :class="{ open: isOpen }"
    >
      <i v-if="!isOpen" class="ti ti-message-chatbot"></i>
      <i v-else class="ti ti-x"></i>
    </button>

    <transition name="chat-slide">
      <div v-if="isOpen" class="chat-window">

        <div class="chat-header">
          <div class="chat-header-info">
            <div class="chat-avatar"><i class="ti ti-robot"></i></div>
            <div>
              <div class="chat-title">Richman AI</div>
              <div class="chat-subtitle">통합 금융 어시스턴트</div>
            </div>
          </div>
          <button class="chat-reset-btn" @click="resetChat" title="대화 초기화">
            <i class="ti ti-refresh"></i>
          </button>
        </div>

        <div class="chat-messages" ref="messagesEl">
          <div v-if="chatStore.messages.length === 0" class="welcome-msg">
            <i class="ti ti-pig-money text-primary mb-2" style="font-size: 32px"></i>
            <p class="font-bold">안녕하세요!</p>
            <p>저는 Richman AI 어시스턴트예요.</p>
            <div class="quick-btns">
              <button @click="quickSend('비트코인 지금 얼마야?')"><i class="ti ti-currency-bitcoin"></i> BTC 시세</button>
              <button @click="quickSend('이더리움 알려줘')"><i class="ti ti-currency-ethereum"></i> ETH 시세</button>
              <button @click="quickSend('이번달 소비 어때?')"><i class="ti ti-receipt"></i> 소비 현황</button>
              <button @click="quickSend('삼성전자 주가 어때?')"><i class="ti ti-chart-line"></i> 주식 시세</button>
            </div>
          </div>

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

          <div v-if="chatStore.isLoading" class="msg-wrapper assistant">
            <div class="msg-bubble assistant loading">
              <span class="dot" /><span class="dot" /><span class="dot" />
            </div>
          </div>
        </div>

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
            <i class="ti ti-send"></i>
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
    crypto: '크립토',
    stock: '주식',
    consumption: '소비',
    price_alert: '알림',
    mixed: '일반',
    finlife: '예적금'
  }
  return map[intent] ?? ''
}

watch(() => chatStore.messages.length, scrollToBottom)
</script>

<style scoped>
/* ── 플로팅 버튼 ── */
.chat-widget {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  font-family: var(--font-main);
}

.chat-toggle-btn {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  border: none;
  cursor: pointer;
  font-size: 24px;
  box-shadow: 0 4px 16px rgba(66, 184, 131, 0.4);
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.chat-toggle-btn:hover { background: var(--color-primary-hover); transform: scale(1.05); }
.chat-toggle-btn.open { background: var(--color-text-secondary); box-shadow: 0 4px 16px rgba(0,0,0,0.1); }

/* ── 채팅창 ── */
.chat-window {
  position: absolute;
  bottom: 68px;
  right: 0;
  width: 360px;
  height: 520px;
  background: var(--color-bg-card);
  border: 0.5px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: 0 8px 32px rgba(0,0,0,0.12);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 헤더 */
.chat-header {
  background: var(--color-primary);
  color: white;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.chat-header-info { display: flex; align-items: center; gap: 10px; }
.chat-avatar { width: 32px; height: 32px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; }
.chat-title { font-weight: 600; font-size: 0.95rem; }
.chat-subtitle { font-size: 0.7rem; opacity: 0.9; }
.chat-reset-btn { background: transparent; border: none; color: white; cursor: pointer; font-size: 18px; opacity: 0.8; transition: opacity 0.15s; }
.chat-reset-btn:hover { opacity: 1; }

/* 메시지 목록 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: var(--color-bg-secondary);
}

/* 웰컴 */
.welcome-msg { text-align: center; color: var(--color-text-secondary); font-size: 0.85rem; padding: 24px 0; }
.text-primary { color: var(--color-primary); }
.mb-2 { margin-bottom: 8px; }
.font-bold { font-weight: 600; color: var(--color-text-primary); font-size: 0.95rem; }
.welcome-msg p { margin: 4px 0; }
.quick-btns { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 16px; }
.quick-btns button { display: inline-flex; align-items: center; gap: 4px; padding: 6px 12px; background: var(--color-bg-card); border: 0.5px solid var(--color-border-strong); border-radius: 20px; font-size: 0.75rem; color: var(--color-text-secondary); cursor: pointer; font-family: var(--font-main); transition: all 0.15s; }
.quick-btns button:hover { background: var(--color-primary-light); color: var(--color-primary); border-color: var(--color-primary); }

/* 메시지 버블 */
.msg-wrapper { display: flex; }
.msg-wrapper.user { justify-content: flex-end; }
.msg-wrapper.assistant { justify-content: flex-start; }

.msg-bubble { max-width: 85%; padding: 10px 14px; border-radius: 14px; font-size: 0.9rem; }
.msg-bubble.user { background: var(--color-primary); color: white; border-bottom-right-radius: 4px; }
.msg-bubble.assistant { background: var(--color-bg-card); color: var(--color-text-primary); border: 0.5px solid var(--color-border); border-bottom-left-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }

.msg-content { margin: 0; white-space: pre-wrap; word-break: break-word; font-family: var(--font-main); font-size: 0.9rem; line-height: 1.5; }

.msg-time { font-size: 0.7rem; color: var(--color-text-tertiary); margin-top: 6px; display: flex; align-items: center; gap: 6px; }
.msg-wrapper.user .msg-time { justify-content: flex-end; color: rgba(255,255,255,0.8); }

.intent-badge { font-size: 0.7rem; font-weight: 600; padding: 2px 6px; background: var(--color-bg-page); color: var(--color-text-secondary); border-radius: 10px; border: 0.5px solid var(--color-border); }
.msg-wrapper.user .intent-badge { background: rgba(0,0,0,0.1); color: white; border: none; }

/* 로딩 */
.loading { display: flex; align-items: center; gap: 4px; padding: 14px 16px; }
.dot { width: 6px; height: 6px; border-radius: 50%; background: var(--color-text-tertiary); animation: bounce 1.2s infinite; }
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%, 80%, 100% { transform: translateY(0); } 40% { transform: translateY(-4px); background: var(--color-primary); } }

/* 입력창 */
.chat-input-area { padding: 12px; border-top: 0.5px solid var(--color-border); display: flex; gap: 8px; align-items: flex-end; background: var(--color-bg-card); }
.chat-input { flex: 1; border: 0.5px solid var(--color-border-strong); border-radius: var(--radius-md); padding: 10px 12px; font-size: 0.9rem; font-family: var(--font-main); resize: none; outline: none; line-height: 1.4; max-height: 120px; overflow-y: auto; background: var(--color-bg-page); transition: border-color 0.15s; }
.chat-input:focus { border-color: var(--color-primary); }

.chat-send-btn { width: 40px; height: 40px; border-radius: var(--radius-md); background: var(--color-primary); border: none; color: white; font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center; flex-shrink: 0; transition: background 0.15s; }
.chat-send-btn:hover:not(:disabled) { background: var(--color-primary-hover); }
.chat-send-btn:disabled { background: var(--color-text-tertiary); cursor: not-allowed; }

/* 슬라이드 애니메이션 */
.chat-slide-enter-active,
.chat-slide-leave-active { transition: all 0.25s ease; }
.chat-slide-enter-from,
.chat-slide-leave-to { opacity: 0; transform: translateY(16px) scale(0.95); }
</style>