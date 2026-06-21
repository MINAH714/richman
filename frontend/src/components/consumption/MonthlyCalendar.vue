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

  <!-- 무지출일 때 가운데 크게 -->
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
  console.log(data)
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

// dailyTotals.value가 아직 로딩 중이거나 값이 없어도 에러를 내지 않고 0을 반환합니다.
const totalOf  = (day) => dailyTotals.value?.[dateStr(day)] || 0


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
  display: flex;
  flex-direction: column;
}
.calendar__cell:hover        { background: #f0f4ff; }
.calendar__cell.is-today     { border-color: #6c63ff; border-width: 2px; }
.calendar__cell.is-no-spend {
  background: #fffbea;
}
.calendar__day    { font-size:.85rem; font-weight:600; }
.calendar__amount { display:block; font-size:.75rem; color:#e05; margin-top:4px; }
.calendar__badge {
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 20px;
  height: 20px;
}
.calendar__no-spend-center {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
.no-spend-icon {
  width: 36px;
  height: 36px;
}

</style>