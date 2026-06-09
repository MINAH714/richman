<template>
  <div class="toast-container">
    <transition-group name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="toast"
        :class="toast.type"
      >
        <span class="toast-icon">{{ toast.type === 'up' ? '🚀' : '📉' }}</span>
        <div class="toast-body">
          <span class="toast-name">{{ toast.name }}</span>
          <span class="toast-msg">{{ toast.message }}</span>
        </div>
        <button class="toast-close" @click="remove(toast.id)">✕</button>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const toasts = ref([])

function add(toast) {
  const id = Date.now()
  toasts.value.push({ id, ...toast })
  // 5초 후 자동 제거
  setTimeout(() => remove(id), 5000)
}

function remove(id) {
  toasts.value = toasts.value.filter(t => t.id !== id)
}

// 부모에서 호출할 수 있도록 expose
defineExpose({ add })
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.toast {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 8px;
  background: white;
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
  min-width: 260px;
  max-width: 340px;
  border-left: 4px solid;
}
.toast.up   { border-color: #ef4444; }
.toast.down { border-color: #3b82f6; }

.toast-icon { font-size: 1.2rem; }

.toast-body {
  display: flex;
  flex-direction: column;
  flex: 1;
}
.toast-name { font-weight: 600; font-size: 0.9rem; }
.toast-msg  { font-size: 0.8rem; color: #6b7280; margin-top: 2px; }

.toast-close {
  background: none;
  border: none;
  cursor: pointer;
  color: #9ca3af;
  font-size: 0.8rem;
  padding: 0;
}
.toast-close:hover { color: #374151; }

/* 애니메이션 */
.toast-enter-active { transition: all 0.3s ease; }
.toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from   { opacity: 0; transform: translateX(40px); }
.toast-leave-to     { opacity: 0; transform: translateX(40px); }
</style>