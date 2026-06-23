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
          {{ totalOf(day).toLocaleString() }}
        </span>
        <div v-if="totalOf(day) === 0 && isPast(day)" class="calendar__no-spend-center">
          <span class="no-spend-mark">0</span>
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
.calendar { max-width: 100%; margin: 0 auto; font-family: 'Inter', sans-serif; }
.calendar__grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background: #e1e3e4;
  border: 1px solid #e1e3e4;
}
.calendar__dow {
  text-align: center;
  font-family: 'Geist', sans-serif;
  font-size: 10px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #4c4546;
  padding: 8px 0;
  background: #ffffff;
}
.calendar__cell,
.calendar__cell--empty {
  min-height: 64px;
  background: #ffffff;
  padding: 6px;
  position: relative;
  display: flex;
  flex-direction: column;
}
.calendar__cell { cursor: pointer; transition: background .12s; }
.calendar__cell:hover { background: #f3f4f5; }
.calendar__cell.is-today {
  box-shadow: inset 0 0 0 2px #0050cc;
}
.calendar__cell.is-no-spend { background: #f8f9fa; }

.calendar__day {
  font-family: 'Geist', sans-serif;
  font-size: .78rem;
  font-weight: 500;
  color: #191c1d;
}
.calendar__amount {
  display: block;
  font-family: 'Hanken Grotesk', sans-serif;
  font-size: .76rem;
  font-weight: 700;
  color: #191c1d;
  margin-top: 4px;
}

.calendar__no-spend-center {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
.no-spend-mark {
  width: 22px;
  height: 22px;
  border: 1px solid #cfc4c5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Hanken Grotesk', sans-serif;
  font-size: .68rem;
  font-weight: 700;
  color: #4c4546;
}
</style>