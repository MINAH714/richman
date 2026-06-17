<!-- src/components/mypage/CalendarTab.vue -->
<template>
  <div class="calendar-tab">
    <MonthlyCalendar @day-click="selectedDate = $event" />
    <DayDetailModal
      v-if="selectedDate"
      :date="selectedDate"
      @close="selectedDate = null"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import MonthlyCalendar from '@/components/consumption/MonthlyCalendar.vue'
import DayDetailModal  from '@/components/consumption/DayDetailModal.vue'

const selectedDate = ref(null)
</script>