<template>
  <div class="calendar-tab">
    <MonthlyCalendar
      :key="`${year}-${month}`"
      :year="year"
      :month="month"
      @day-click="selectedDate = $event"
    />
    <DayDetailModal
      v-if="selectedDate"
      :date="selectedDate"
      @close="selectedDate = null"
      @settle-changed="$emit('settle-changed')"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import MonthlyCalendar from '@/components/consumption/MonthlyCalendar.vue'
import DayDetailModal  from '@/components/consumption/DayDetailModal.vue'

defineProps({
  year:  { type: Number, required: true },
  month: { type: Number, required: true },
})

const emit = defineEmits(['settle-changed'])   // ← 추가

const selectedDate = ref(null)
</script>