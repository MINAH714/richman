<!-- src/components/consumption/MonthlyCalendar.vue -->
<template>
  <div class="calendar">
    <div class="calendar__header">
      <button @click="prevMonth">◀</button>
      <h2>{{ year }}년 {{ month }}월</h2>
      <button @click="nextMonth">▶</button>
    </div>

    <div class="calendar__grid">
      <div class="calendar__dow" v-for="d in DOW" :key="d">{{ d }}</div>

      <!-- 빈 칸 (월 시작 전) -->
      <div v-for="n in startBlank" :key="'b'+n" class="calendar__cell--empty" />

      <!-- 날짜 셀 -->
      <div
        v-for="day in daysInMonth"
        :key="day"
        class="calendar__cell"
        :class="{
          'is-today':    isToday(day),
          'is-no-spend': totalOf(day) === 0 && isPast(day),
        }"
        @click="emit('day-click', dateStr(day))"
      >
        <span class="calendar__day">{{ day }}</span>
        <span v-if="totalOf(day) > 0" class="calendar__amount">
          {{ totalOf(day).toLocaleString() }}원
        </span>
        <!-- 무지출 배지 -->
        <span v-if="totalOf(day) === 0 && isPast(day)" class="calendar__badge">
          🌟
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { getMonthlyCalendar } from '@/api/consumption'

const emit = defineEmits(['day-click'])

const DOW = ['일', '월', '화', '수', '목', '금', '토']

const today = new Date()
const year  = ref(today.getFullYear())
const month = ref(today.getMonth() + 1)

const dailyTotals = ref({})   // { '2025-06-03': 15000, ... }

const fetchCalendar = async () => {
  const { data } = await getMonthlyCalendar(year.value, month.value)
  dailyTotals.value = data.daily_totals
}

onMounted(fetchCalendar)
watch([year, month], fetchCalendar)

// 해당 월의 1일이 무슨 요일인지
const startBlank = computed(() =>
  new Date(year.value, month.value - 1, 1).getDay()
)

const daysInMonth = computed(() =>
  new Date(year.value, month.value, 0).getDate()  // 0일 = 전달 마지막날
)

const dateStr  = (day) =>
  `${year.value}-${String(month.value).padStart(2,'0')}-${String(day).padStart(2,'0')}`

const totalOf  = (day) => dailyTotals.value[dateStr(day)] || 0


const isToday  = (day) =>
  today.getFullYear() === year.value &&
  today.getMonth() + 1 === month.value &&
  today.getDate() === day

const isPast   = (day) =>
  new Date(year.value, month.value - 1, day) < today

const prevMonth = () => {
  if (month.value === 1) { year.value--; month.value = 12 }
  else month.value--
}
const nextMonth = () => {
  if (month.value === 12) { year.value++; month.value = 1 }
  else month.value++
}
</script>

<style scoped>
.calendar { max-width: 720px; margin: 0 auto; font-family: sans-serif; }
.calendar__header { display:flex; justify-content:space-between; align-items:center; padding:1rem; }
.calendar__grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}
.calendar__dow  { text-align:center; font-size:.8rem; color:#888; padding:.4rem 0; }
.calendar__cell {
  min-height: 70px;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 6px;
  cursor: pointer;
  transition: background .15s;
  position: relative;
}
.calendar__cell:hover        { background: #f0f4ff; }
.calendar__cell.is-today     { border-color: #6c63ff; border-width: 2px; }
.calendar__cell.is-no-spend  { background: #fffbea; }
.calendar__day    { font-size:.85rem; font-weight:600; }
.calendar__amount { display:block; font-size:.75rem; color:#e05; margin-top:4px; }
.calendar__badge  { position:absolute; bottom:4px; right:4px; font-size:1rem; }
</style>