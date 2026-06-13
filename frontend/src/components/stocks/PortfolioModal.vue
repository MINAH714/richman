<!-- src/components/stocks/PortfolioModal.vue -->
<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-box">
      <h3>포트폴리오 입력</h3>
      <p class="modal-symbol">{{ symbol }} · {{ name }}</p>

      <div class="form-group">
        <label>보유 수량</label>
        <input
          v-model.number="form.quantity"
          type="number"
          min="0"
          step="0.0001"
          placeholder="예: 10"
        />
      </div>

      <div class="form-group">
        <label>평균 매입가 (원 또는 USD)</label>
        <input
          v-model.number="form.average_price"
          type="number"
          min="0"
          step="0.01"
          placeholder="예: 75000"
        />
      </div>

      <div class="modal-actions">
        <button class="btn-cancel" @click="$emit('close')">취소</button>
        <button class="btn-save" @click="handleSave" :disabled="!isValid">저장</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// 부모 컴포넌트에서 받을 데이터
const props = defineProps({
  watchlistId: { type: Number, required: true },
  symbol:      { type: String, required: true },
  name:        { type: String, required: true },
  existing:    { type: Object, default: null },  // 기존 포트폴리오 (수정 시)
})

// 부모에게 보낼 이벤트
const emit = defineEmits(['close', 'saved'])

// 폼 입력값 (기존 데이터가 있으면 미리 채워줌)
const form = ref({
  quantity:      props.existing?.quantity      ?? '',
  average_price: props.existing?.average_price ?? '',
})

// 저장 버튼 활성화 조건
const isValid = computed(() =>
  form.value.quantity > 0 && form.value.average_price > 0
)

function handleSave() {
  // 부모 컴포넌트로 저장 이벤트 + 입력값 전달
  emit('saved', {
    watchlistId: props.watchlistId,
    data: {
      quantity:      form.value.quantity,
      average_price: form.value.average_price,
    }
  })
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-box {
  background: #fff;
  border-radius: 12px;
  padding: 28px;
  width: 340px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
}
.modal-box h3 { margin: 0 0 4px; font-size: 18px; }
.modal-symbol { color: #888; font-size: 13px; margin-bottom: 20px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 13px; color: #555; margin-bottom: 6px; }
.form-group input {
  width: 100%; padding: 10px 12px;
  border: 1px solid #ddd; border-radius: 8px;
  font-size: 15px; box-sizing: border-box;
}
.modal-actions { display: flex; gap: 10px; margin-top: 24px; }
.btn-cancel {
  flex: 1; padding: 10px; border: 1px solid #ddd;
  border-radius: 8px; background: #f5f5f5; cursor: pointer;
}
.btn-save {
  flex: 1; padding: 10px; border: none;
  border-radius: 8px; background: #2563eb; color: #fff;
  cursor: pointer; font-weight: 600;
}
.btn-save:disabled { background: #aaa; cursor: not-allowed; }
</style>