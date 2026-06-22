<template>
  <div class="chat-page">
    <div class="section-inner">
      <header class="page-header">
        <div class="header-text">
          <p class="eyebrow">AI ASSISTANT</p>
          <h1 class="page-title">Richman AI 어시스턴트</h1>
          <p class="page-desc">암호화폐 · 주식 · 소비 통합 금융 어시스턴트</p>
        </div>
        <button class="btn btn-outline" @click="resetChat">
          <i class="ti ti-refresh" aria-hidden="true"></i> 대화 초기화
        </button>
      </header>

      <div v-if="!authStore.isLoggedIn" class="empty-state">
        <i class="ti ti-message-chatbot" aria-hidden="true"></i>
        <p>챗봇 기능은 로그인 후 이용할 수 있어요!</p>
        <router-link to="/login" class="btn btn-primary mt-3">로그인하러 가기</router-link>
      </div>

      <div v-else class="chat-layout">
        <div class="chat-main">
          <div class="chat-messages" ref="messagesEl">
            <div v-if="chatStore.messages.length === 0" class="welcome-section">
              <div class="welcome-icon"><i class="ti ti-robot"></i></div>
              <h2>안녕하세요!</h2>
              <p>무엇이든 물어보세요. 실시간 데이터를 기반으로 답변해드릴게요.</p>

              <div class="quick-grid">
                <button
                  v-for="q in quickQuestions"
                  :key="q.text"
                  class="quick-card"
                  @click="quickSend(q.text)"
                >
                  <span class="quick-icon"><i :class="q.icon"></i></span>
                  <span class="quick-text">{{ q.text }}</span>
                </button>
              </div>
            </div>

            <div
              v-for="msg in chatStore.messages"
              :key="msg.id"
              class="msg-wrapper"
              :class="msg.role"
            >
              <div v-if="msg.role === 'assistant'" class="msg-avatar">
                <i class="ti ti-robot"></i>
              </div>

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

            <div v-if="chatStore.isLoading" class="msg-wrapper assistant">
              <div class="msg-avatar"><i class="ti ti-robot"></i></div>
              <div class="msg-bubble assistant loading-bubble">
                <span class="dot" /><span class="dot" /><span class="dot" />
              </div>
            </div>
          </div>

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
              class="btn btn-primary send-btn"
              @click="handleSend"
              :disabled="!inputText.trim() || chatStore.isLoading"
            >
              <i class="ti ti-send"></i> 전송
            </button>
          </div>
        </div>

        <aside class="chat-sidebar">
          <div class="sidebar-section">
            <h3><i class="ti ti-bulb text-primary"></i> 추천 질문</h3>
            <div class="suggest-list">
              <button
                v-for="q in quickQuestions"
                :key="q.text"
                class="suggest-btn"
                @click="quickSend(q.text)"
              >
                <i :class="q.icon"></i> {{ q.text }}
              </button>
            </div>
          </div>

          <div class="sidebar-section">
            <h3><i class="ti ti-pin text-primary"></i> 사용 가이드</h3>
            <ul class="guide-list">
              <li><i class="ti ti-currency-bitcoin"></i> <strong>코인 시세</strong>: "비트코인 얼마야?"</li>
              <li><i class="ti ti-bell"></i> <strong>가격 알림</strong>: "BTC 1억 되면 알려줘"</li>
              <li><i class="ti ti-chart-candle"></i> <strong>주식 조회</strong>: "삼성전자 주가 어때?"</li>
              <li><i class="ti ti-receipt"></i> <strong>소비 분석</strong>: "이번달 식비 얼마야?"</li>
            </ul>
          </div>
        </aside>
      </div>
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
  { icon: 'ti ti-currency-bitcoin', text: '비트코인 지금 얼마야?' },
  { icon: 'ti ti-currency-ethereum', text: '이더리움 시세 알려줘' },
  { icon: 'ti ti-bell', text: '비트코인 1억 되면 알려줘' },
  { icon: 'ti ti-chart-line', text: '삼성전자 주가 어때?' },
  { icon: 'ti ti-receipt', text: '이번달 소비 현황 알려줘' },
  { icon: 'ti ti-flame', text: '요즘 핫한 코인 뭐야?' },
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
    crypto: '크립토',
    stock: '주식',
    consumption: '소비',
    price_alert: '알림',
    mixed: '일반',
    finlife: '예적금'
  }
  return map[intent] ?? intent
}

watch(() => chatStore.messages.length, scrollToBottom)
</script>

<style scoped>
.chat-page {
  min-height: calc(100vh - 56px);
  background: var(--color-bg-page);
  font-family: var(--font-main);
  color: var(--color-text-primary);
  padding: 40px 0 80px;
}

.section-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px;
}

/* ── 헤더 ── */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
  flex-wrap: wrap;
  gap: 16px;
}
.eyebrow { font-size: 12px; font-weight: 600; letter-spacing: 0.1em; color: var(--color-primary); margin: 0 0 10px; }
.page-title { font-size: 2rem; font-weight: 700; line-height: 1.35; margin: 0 0 8px; letter-spacing: -0.02em; }
.page-desc { font-size: 0.95rem; color: var(--color-text-secondary); line-height: 1.6; margin: 0; }

.btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 10px 18px; border-radius: var(--radius-md); font-size: 0.9rem; font-weight: 600; font-family: var(--font-main); cursor: pointer; transition: all 0.15s; text-decoration: none; border: none; }
.btn-primary { background: var(--color-primary); color: white; }
.btn-primary:hover:not(:disabled) { background: var(--color-primary-hover); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-outline { background: var(--color-bg-card); color: var(--color-text-primary); border: 0.5px solid var(--color-border-strong); }
.btn-outline:hover { background: var(--color-bg-secondary); }

/* ── 빈 상태 ── */
.empty-state { text-align: center; padding: 60px 0; color: var(--color-text-tertiary); background: var(--color-bg-card); border: 0.5px dashed var(--color-border-strong); border-radius: var(--radius-lg); }
.empty-state i { font-size: 32px; margin-bottom: 12px; display: block; color: var(--color-text-tertiary); }
.mt-3 { margin-top: 16px; }

/* ── 레이아웃 ── */
.chat-layout {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 24px;
  height: calc(100vh - 220px);
  min-height: 500px;
}

/* ── 채팅 메인 영역 ── */
.chat-main {
  display: flex;
  flex-direction: column;
  background: var(--color-bg-card);
  border: 0.5px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: var(--color-bg-secondary);
}

/* 웰컴 섹션 */
.welcome-section { text-align: center; padding: 32px 16px; color: var(--color-text-primary); }
.welcome-icon i { font-size: 48px; color: var(--color-primary); margin-bottom: 12px; display: inline-block; }
.welcome-section h2 { font-size: 1.3rem; margin: 0 0 8px; font-weight: 700; }
.welcome-section p { color: var(--color-text-secondary); font-size: 0.9rem; margin-bottom: 24px; }

.quick-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; max-width: 500px; margin: 0 auto; }
.quick-card { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 16px 12px; background: var(--color-bg-card); border: 0.5px solid var(--color-border-strong); border-radius: var(--radius-md); cursor: pointer; font-size: 0.8rem; font-weight: 500; font-family: var(--font-main); transition: all 0.15s; color: var(--color-text-secondary); }
.quick-card:hover { border-color: var(--color-primary); color: var(--color-primary); background: var(--color-primary-light); transform: translateY(-2px); }
.quick-icon i { font-size: 20px; }

/* 메시지 버블 */
.msg-wrapper { display: flex; align-items: flex-end; gap: 12px; }
.msg-wrapper.user { justify-content: flex-end; }
.msg-wrapper.assistant { justify-content: flex-start; }

.msg-avatar { width: 32px; height: 32px; border-radius: 50%; background: var(--color-bg-card); border: 0.5px solid var(--color-border); display: flex; align-items: center; justify-content: center; font-size: 18px; color: var(--color-primary); flex-shrink: 0; }

.msg-bubble { max-width: 75%; padding: 14px 18px; border-radius: 16px; font-size: 0.95rem; }
.msg-bubble.user { background: var(--color-primary); color: white; border-bottom-right-radius: 4px; }
.msg-bubble.assistant { background: var(--color-bg-card); border: 0.5px solid var(--color-border); color: var(--color-text-primary); border-bottom-left-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }

.msg-content { margin: 0; white-space: pre-wrap; word-break: break-word; font-family: var(--font-main); line-height: 1.6; }

.msg-meta { display: flex; align-items: center; gap: 8px; margin-top: 8px; }
.msg-time { font-size: 0.75rem; color: var(--color-text-tertiary); }

.intent-tag { font-size: 0.7rem; padding: 2px 8px; border-radius: 12px; font-weight: 600; background: var(--color-bg-secondary); border: 0.5px solid var(--color-border); color: var(--color-text-secondary); }
.intent-tag.crypto { color: #d97706; background: #fef3c7; border-color: #fde68a; }
.intent-tag.stock { color: #16a34a; background: #dcfce7; border-color: #bbf7d0; }
.intent-tag.consumption { color: #db2777; background: #fce7f3; border-color: #fbcfe8; }
.intent-tag.price_alert { color: #7c3aed; background: #ede9fe; border-color: #ddd6fe; }
.intent-tag.finlife { color: #0284c7; background: #e0f2fe; border-color: #bae6fd; }

/* 로딩 */
.loading-bubble { display: flex; align-items: center; gap: 6px; padding: 16px 20px; }
.dot { width: 6px; height: 6px; border-radius: 50%; background: var(--color-text-tertiary); animation: bounce 1.2s infinite; }
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%, 80%, 100% { transform: translateY(0); } 40% { transform: translateY(-6px); background: var(--color-primary); } }

/* 입력창 */
.chat-input-area { padding: 16px; border-top: 0.5px solid var(--color-border); display: flex; gap: 12px; align-items: flex-end; background: var(--color-bg-card); }
.chat-input { flex: 1; border: 0.5px solid var(--color-border-strong); border-radius: var(--radius-md); padding: 12px 16px; font-size: 0.95rem; font-family: var(--font-main); resize: none; outline: none; line-height: 1.5; max-height: 160px; background: var(--color-bg-page); transition: border-color 0.15s; }
.chat-input:focus { border-color: var(--color-primary); }
.send-btn { border-radius: var(--radius-md); padding: 12px 20px; }

/* ── 사이드바 ── */
.chat-sidebar { display: flex; flex-direction: column; gap: 20px; }
.sidebar-section { background: var(--color-bg-card); border: 0.5px solid var(--color-border); border-radius: var(--radius-lg); padding: 20px; }
.sidebar-section h3 { font-size: 0.95rem; font-weight: 600; margin: 0 0 16px; color: var(--color-text-primary); display: flex; align-items: center; gap: 6px; }
.text-primary { color: var(--color-primary); }

.suggest-list { display: flex; flex-direction: column; gap: 8px; }
.suggest-btn { text-align: left; padding: 10px 12px; background: var(--color-bg-secondary); border: 0.5px solid var(--color-border-strong); border-radius: var(--radius-md); font-size: 0.85rem; font-family: var(--font-main); cursor: pointer; color: var(--color-text-secondary); transition: all 0.15s; display: flex; align-items: center; gap: 8px; }
.suggest-btn:hover { background: var(--color-primary-light); color: var(--color-primary); border-color: var(--color-primary); }

.guide-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 12px; font-size: 0.85rem; color: var(--color-text-secondary); }
.guide-list li { display: flex; align-items: center; gap: 8px; }
.guide-list li i { font-size: 16px; color: var(--color-text-tertiary); }
.guide-list li strong { color: var(--color-text-primary); font-weight: 600; }

@media (max-width: 768px) {
  .chat-layout { grid-template-columns: 1fr; height: auto; }
  .chat-main { height: 60vh; }
  .quick-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>