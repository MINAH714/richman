<!-- src/components/consumption/MonthlyCalendar.vue -->
<template>
  <div class="calendar">
    <div class="calendar__grid">
      <div class="calendar__dow" v-for="d in DOW" :key="d">{{ d }}</div>
      <div v-for="n in startBlank" :key="'b'+n" class="calendar__cell--empty" />

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
        <div v-if="totalOf(day) === 0 && isPast(day)" class="calendar__no-spend-center">
          <svg viewBox="0 0 100 100" class="no-spend-icon">
            <circle cx="50" cy="52" r="34" fill="#FBBF24" stroke="#D97706" stroke-width="2.5" />
            <circle cx="50" cy="52" r="27" fill="none" stroke="#FFFFFF" stroke-width="1.5" stroke-dasharray="2.5 4" opacity="0.6" />
            <text x="50" y="58" text-anchor="middle" font-size="26" font-weight="700" fill="#92400E">0</text>
            <path d="M22 18 L25 26 L33 27 L27 33 L29 41 L22 36 L15 41 L17 33 L11 27 L19 26 Z" fill="#FCD34D" stroke="#D97706" stroke-width="1" />
            <path d="M80 22 L82 28 L88 29 L83 33 L85 39 L80 35 L75 39 L77 33 L72 29 L78 28 Z" fill="#FCD34D" stroke="#D97706" stroke-width="1" />
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted } from 'vue'
import { getMonthlyCalendar } from '@/api/consumption'

const props = defineProps({
  year:  { type: Number, required: true },
  month: { type: Number, required: true },
})
const emit = defineEmits(['day-click'])

const DOW = ['일', '월', '화', '수', '목', '금', '토']
const today = new Date()
const dailyTotals = ref({})

const fetchCalendar = async () => {
  const { data } = await getMonthlyCalendar(props.year, props.month)
  dailyTotals.value = data.daily_totals
}

onMounted(fetchCalendar)
watch(() => [props.year, props.month], fetchCalendar)

const startBlank = computed(() =>
  new Date(props.year, props.month - 1, 1).getDay()
)
const daysInMonth = computed(() =>
  new Date(props.year, props.month, 0).getDate()
)

const dateStr  = (day) =>
  `${props.year}-${String(props.month).padStart(2,'0')}-${String(day).padStart(2,'0')}`
const totalOf  = (day) => dailyTotals.value[dateStr(day)] || 0
const isToday  = (day) =>
  today.getFullYear() === props.year &&
  today.getMonth() + 1 === props.month &&
  today.getDate() === day
const isPast   = (day) =>
  new Date(props.year, props.month - 1, day) < today
</script>

<style scoped>
.calendar { max-width: 100%; margin: 0 auto; font-family: 'IBM Plex Mono', monospace; }
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
  display: flex;
  flex-direction: column;
}
.calendar__cell:hover        { background: #f0f4ff; }
.calendar__cell.is-today     { border-color: #6c63ff; border-width: 2px; }
.calendar__cell.is-no-spend  { background: #fffbea; }
.calendar__day    { font-size:.85rem; font-weight:600; }
.calendar__amount { display:block; font-size:.75rem; color:#e05; margin-top:4px; }
.calendar__no-spend-center {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
.no-spend-icon { width: 36px; height: 36px; }
</style>