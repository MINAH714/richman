<template>

  <div class="commodities-page">

    <header class="page-header">

      <h2 class="page-title">

        <i class="ti ti-chart-line" aria-hidden="true"></i>

        현물 자산 시세 대시보드

      </h2>

      <p class="page-subtitle">국제 금(Gold) 및 은(Silver)의 과거 시세 변동 추이를 확인할 수 있습니다.</p>

    </header>

   

    <div class="control-panel">

      <div class="asset-toggle-group">

        <button

          :class="{ active: selectedAsset === 'gold' }"

          @click="selectedAsset = 'gold'"

          class="btn-toggle btn-gold"

        >

          👑 금 (Gold)

        </button>

        <button

          :class="{ active: selectedAsset === 'silver' }"

          @click="selectedAsset = 'silver'"

          class="btn-toggle btn-silver"

        >

          🥈 은 (Silver)

        </button>

      </div>



      <div class="date-filter-group">

        <label for="start-date" class="visually-hidden">시작일</label>

        <input type="date" id="start-date" v-model="startDate" class="input-date">

        <span class="date-separator">~</span>

        <label for="end-date" class="visually-hidden">종료일</label>

        <input type="date" id="end-date" v-model="endDate" class="input-date">

        <button class="btn-reset" @click="resetDates" title="날짜 초기화">🔄 초기화</button>

      </div>

    </div>



    <div class="chart-container">

      <div v-if="loading" class="status-wrapper">

        <div class="spinner"></div>

        <p>백엔드에서 엑셀 데이터를 정제하는 중입니다...</p>

      </div>

     

      <div v-else-if="chartData" class="chart-wrapper">

        <Line :data="chartData" :options="chartOptions" :key="selectedAsset + startDate + endDate" />

      </div>

     

      <div v-else class="status-wrapper error">

        <p>⚠️ 표시할 시세 데이터가 없습니다. 날짜 범위를 확인해 주세요.</p>

      </div>

    </div>

  </div>

</template>



<script setup>

import { ref, computed, onMounted, watch } from 'vue'

import { Line } from 'vue-chartjs'

import {

  Chart as ChartJS,

  CategoryScale,

  LinearScale,

  PointElement,

  LineElement,

  Title,

  Tooltip,

  Legend

} from 'chart.js'

import axios from 'axios'



// Chart.js 필수 컴포넌트 등록

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)



const selectedAsset = ref('gold')

const startDate = ref('')

const endDate = ref('')

const rawData = ref([])

const loading = ref(false)



// 백엔드 Django API 호출 함수

const fetchData = async () => {

  loading.value = true

  try {

    const response = await axios.get(`http://localhost:8000/api/commodities/${selectedAsset.value}/`)

    rawData.value = response.data

  } catch (error) {

    console.error("현물 데이터 로드 실패:", error)

    rawData.value = []

  } finally {

    loading.value = false

  }

}



// 자산 토글이 바뀔 때마다 자동으로 백엔드 데이터를 새로 불러옵니다.

watch(selectedAsset, () => {

  fetchData()

})



onMounted(() => {

  fetchData()

})



// 날짜 초기화 기능

function resetDates() {

  startDate.value = ''

  endDate.value = ''

}



// 요구사항 ③: 시작일과 종료일 필터링 로직 (선택하지 않으면 전체 기간 데이터를 보여준다.)

const filteredData = computed(() => {

  // 예외 방어: 백엔드 에러로 인해 rawData가 배열이 아닐 경우 빈 배열 반환

  if (!rawData.value || !Array.isArray(rawData.value)) {

    return []

  }

 

  // 🎯 날짜를 고르지 않았을 때는 복잡한 가치 비교를 건너뛰고 107개 원본 데이터를 즉시 통으로 리턴합니다.

  if (!startDate.value && !endDate.value) {

    return rawData.value

  }

 

  // 시작일 또는 종료일이 하나라도 걸려있을 때만 안전하게 타임스탬프 숫자화하여 필터 연산 진행

  return rawData.value.filter(item => {

    if (!item.Date) return false

   

    let pass = true

    const itemTime = new Date(item.Date).getTime()

   

    if (startDate.value) {

      pass = pass && itemTime >= new Date(startDate.value).getTime()

    }

    if (endDate.value) {

      pass = pass && itemTime <= new Date(endDate.value).getTime()

    }

    return pass

  })

})



// Chart.js 바인딩용 반응형 데이터셋 구조

const chartData = computed(() => {

  if (filteredData.value.length === 0) return null



  const isGold = selectedAsset.value === 'gold'

 

  return {

    labels: filteredData.value.map(item => item.Date),

    datasets: [

      {

        label: `${isGold ? '금(Gold)' : '은(Silver)'} 종가 ($)`,

        backgroundColor: isGold ? 'rgba(218, 165, 32, 0.1)' : 'rgba(192, 192, 192, 0.1)',

        borderColor: isGold ? '#DAA520' : '#94a3b8',

        pointBackgroundColor: isGold ? '#B8860B' : '#64748b',

        data: filteredData.value.map(item => item.Price),

        tension: 0.15,

        fill: true

      }

    ]

  }

})



// 차트 세부 옵션 커스텀 설정

const chartOptions = {

  responsive: true,

  maintainAspectRatio: false,

  plugins: {

    legend: {

      position: 'top',

      labels: {

        font: { family: 'sans-serif', size: 12, weight: '600' }

      }

    },

    tooltip: {

      padding: 12,

      cornerRadius: 8

    }

  },

  scales: {

    x: {

      grid: { display: false },

      ticks: {

        maxRotation: 0,      // 대각선 회전 절대 방지

        minRotation: 0,      // 가로 정렬 고정

        autoSkip: true,      // 중간 라벨들은 겹치지 않게 스킵

        autoSkipPadding: 40, // 라벨 간격 여유를 대폭 늘려서 마지막 글자가 들어갈 공간 확보

       

        // 🎯 [핵심] 마지막 라벨이 공간 부족으로 지워지는 걸 방지하는 핵심 속성 2개 추가

        includeBounds: true, // 축의 맨 첫 번째와 맨 마지막 데이터를 라벨에 무조건 포함하도록 지시

        preserveSampleDensity: false,

       

        callback: function(val, index, clicks) {

          const label = this.getLabelForValue(val);

         

          // 첫 번째 데이터이거나 마지막 데이터(24년 12월 1일 등)이면 무조건 글자 리턴

          if (index === 0 || index === clicks.length - 1) {

            return label;

          }

         

          return label;

        }

      }

    },

    y: {

      ticks: {

        callback: function(value) {

          return '$' + value.toLocaleString()

        }

      }

    }

  }

}

</script>


<style scoped>
.commodities-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px 24px;
  font-family: var(--font-main, sans-serif);
  box-sizing: border-box; /* 🎯 모든 요소의 너비 계산 방식을 테두리 기준으로 통일 */
}

/* 꼼꼼한 너비 계산을 위한 전역 규칙 상속 */
.commodities-page * {
  box-sizing: border-box;
}

.page-header {
  margin-bottom: 28px;
  padding-left: 4px; /* 타이틀 라인을 정돈하기 위한 미세 조정 */
}
.page-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 6px;
}
.page-subtitle {
  font-size: 0.88rem;
  color: #64748b;
  margin: 0;
}

/* 🎯 컨트롤 패널 (상단 배너) 스타일 교정 */
.control-panel {
  width: 100%; /* 부모 너비인 1100px에 100% 핏 */
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 24px;
  background: #f8fafc;
  padding: 16px 20px;
  border-radius: 12px;
  border: 1px solid #edf2f7;
}

/* 자산 토글 스위치 버튼군 스타일 */
.asset-toggle-group {
  display: flex;
  gap: 8px;
}
.btn-toggle {
  padding: 10px 20px;
  font-size: 0.9rem;
  font-weight: 600;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-gold:hover { border-color: #DAA520; color: #DAA520; }
.btn-gold.active { background: #DAA520; color: white; border-color: #DAA520; }
.btn-silver:hover { border-color: #94a3b8; color: #64748b; }
.btn-silver.active { background: #94a3b8; color: white; border-color: #94a3b8; }

/* 날짜 필터 인풋 스타일 */
.date-filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}
.input-date {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.88rem;
  color: #1e293b;
  outline: none;
}
.input-date:focus { border-color: #3b6fd4; }
.date-separator { font-size: 0.9rem; color: #94a3b8; }
.btn-reset {
  padding: 8px 12px;
  background: #fff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.85rem;
  cursor: pointer;
  color: #64748b;
}
.btn-reset:hover { background: #f1f5f9; color: #1e293b; }

/* 🎯 차트 내부 박스 스타일 교정 */
.chart-container {
  width: 100%; /* 🚀 패널과 완전히 동일하게 100% 너비 수렴 */
  height: 480px;
  background: white;
  border: 1px solid #edf2f7;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
  display: flex;
  align-items: center;
  justify-content: center;
}
.chart-wrapper {
  width: 100%;
  height: 100%;
}

/* 로딩 애니메이션 및 오류 바운더리 구역 스타일 */
.status-wrapper {
  text-align: center;
  color: #64748b;
  font-size: 0.9rem;
}
.status-wrapper.error { color: #ef4444; }
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f1f5f9;
  border-top-color: #3b6fd4;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
.visually-hidden { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); border: 0; }

@media (max-width: 768px) {
  .control-panel { flex-direction: column; align-items: stretch; }
  .asset-toggle-group { display: grid; grid-template-columns: 1fr 1fr; }
  .date-filter-group { justify-content: space-between; }
}
</style>