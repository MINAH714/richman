<!-- src/views/ConsumptionView.vue -->
<template>
  <div class="consumption-wrap">
    <MonthlyCalendar @day-click="onDayClick" />
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
const onDayClick = (date) => { selectedDate.value = date }
</script>