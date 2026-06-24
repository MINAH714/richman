<template>
  <div class="compare-page">
    <div class="page-header">
      <h1 class="page-title">🪙 코인 비교</h1>
      <p class="page-desc">최대 3개의 코인을 선택해서 시세와 30일 추이를 비교해보세요.</p>
    </div>

    <!-- 코인 선택 영역 -->
    <section class="select-section">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="코인명, 심볼 검색..."
        class="search-input"
      />

      <div class="selected-chips" v-if="selectedMarkets.length > 0">
        <span v-for="market in selectedMarkets" :key="market" class="chip">
          {{ coinLabel(market) }}
          <button class="chip-remove" @click="toggleSelect(market)">✕</button>
        </span>
      </div>

      <div v-if="isLoadingCoins" class="loading">코인 목록을 불러오는 중...</div>
      <div v-else class="coin-grid">
        <button
          v-for="coin in filteredCoins"
          :key="coin.market"
          class="coin-pick"
          :class="{ active: selectedMarkets.includes(coin.market) }"
          :disabled="!selectedMarkets.includes(coin.market) && selectedMarkets.length >= MAX_COINS"
          @click="toggleSelect(coin.market)"
        >
          <span class="pick-kor">{{ coin.korean_name }}</span>
          <span class="pick-sym">{{ coin.coin_symbol }}</span>
        </button>
      </div>
    </section>

    <p v-if="selectedMarkets.length >= MAX_COINS" class="limit-msg">
      최대 {{ MAX_COINS }}개까지 비교할 수 있어요.
    </p>

    <!-- 비교 결과 -->
    <section v-if="isComparing" class="loading result-loading">비교 데이터를 불러오는 중...</section>

    <section v-else-if="compareData" class="result-section">
      <h2 class="section-title">시세 비교</h2>
      <table class="compare-table">
        <thead>
          <tr>
            <th>코인</th>
            <th class="text-right">현재가</th>
            <th class="text-right">등락률</th>
            <th class="text-right">거래대금(24h)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="coin in compareData.coins" :key="coin.market">
            <td class="name-cell">
              <span class="kor">{{ coin.korean_name }}</span>
              <span class="eng">{{ coin.coin_symbol }}</span>
            </td>
            <td class="text-right">{{ formatPrice(coin.trade_price) }}</td>
            <td class="text-right" :class="changeClass(coin.change)">
              {{ formatRate(coin.change_rate, coin.change) }}
            </td>
            <td class="text-right">{{ formatVolume(coin.acc_trade_price_24h) }}</td>
          </tr>
        </tbody>
      </table>

      <h2 class="section-title chart-title">30일 종가 추이</h2>
      <div class="chart-wrap">
        <VueApexCharts
          type="line"
          height="380"
          :options="chartOptions"
          :series="chartSeries"
        />
      </div>
    </section>

    <section v-else class="empty-state">
      <p>코인을 1개 이상 선택하면 비교 결과가 표시됩니다.</p>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import VueApexCharts from 'vue3-apexcharts'
import { cryptoAPI } from '@/api/crypto'

const MAX_COINS = 3

// ── 코인 목록 (선택 UI용) ─────────────────────────────
const allCoins = ref([])
const isLoadingCoins = ref(true)
const searchQuery = ref('')

const filteredCoins = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return allCoins.value
  return allCoins.value.filter(c =>
    c.korean_name.toLowerCase().includes(q) ||
    c.english_name.toLowerCase().includes(q) ||
    c.coin_symbol.toLowerCase().includes(q)
  )
})

function coinLabel(market) {
  const coin = allCoins.value.find(c => c.market === market)
  return coin ? `${coin.korean_name} (${coin.coin_symbol})` : market
}

async function loadCoins() {
  try {
    const { data } = await cryptoAPI.getCoins()
    allCoins.value = data
  } catch (e) {
    console.error('코인 목록 로드 실패:', e)
  } finally {
    isLoadingCoins.value = false
  }
}

// ── 선택 (최대 3개) ──────────────────────────────────────
const selectedMarkets = ref([])

function toggleSelect(market) {
  const idx = selectedMarkets.value.indexOf(market)
  if (idx >= 0) {
    selectedMarkets.value.splice(idx, 1)
  } else if (selectedMarkets.value.length < MAX_COINS) {
    selectedMarkets.value.push(market)
  }
}

// ── 비교 데이터 조회 ─────────────────────────────────────
const compareData = ref(null)
const isComparing = ref(false)
let debounceTimer = null

async function fetchCompare() {
  if (selectedMarkets.value.length === 0) {
    compareData.value = null
    return
  }
  isComparing.value = true
  try {
    const { data } = await cryptoAPI.compareCoins(selectedMarkets.value)
    compareData.value = data
  } catch (e) {
    console.error('코인 비교 조회 실패:', e)
    compareData.value = null
  } finally {
    isComparing.value = false
  }
}

watch(selectedMarkets, () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(fetchCompare, 300)
}, { deep: true })

onMounted(() => {
  loadCoins()
})

// ── 차트 ──────────────────────────────────────────────
const chartSeries = computed(() => {
  if (!compareData.value) return []
  return compareData.value.coins.map(coin => ({
    name: coin.korean_name,
    data: coin.candles.map(c => c.trade_price),
  }))
})

const chartOptions = computed(() => ({
  chart: {
    toolbar: { show: false },
    zoom: { enabled: false },
  },
  stroke: { width: 2.5, curve: 'smooth' },
  xaxis: {
    categories: compareData.value?.coins?.[0]?.candles.map(c => c.date.slice(5)) ?? [],
    labels: { style: { fontSize: '11px' } },
  },
  yaxis: {
    labels: {
      formatter: (val) => val?.toLocaleString('ko-KR'),
    },
  },
  colors: ['#2563eb', '#ef4444', '#f59e0b'],
  legend: { position: 'top' },
  tooltip: {
    y: { formatter: (val) => val?.toLocaleString('ko-KR') + '원' },
  },
}))

// ── 포맷 헬퍼 ─────────────────────────────────────────
function formatPrice(price) {
  if (price == null) return '-'
  return price >= 100 ? price.toLocaleString('ko-KR') + ' 원' : price.toFixed(4) + ' 원'
}

function formatRate(rate, change) {
  if (rate == null) return '-'
  if (change === 'EVEN' || Math.abs(rate) < 0.000001) return '0.00%'
  const sign = change === 'RISE' ? '+' : '-'
  return sign + (Math.abs(rate) * 100).toFixed(2) + '%'
}

function changeClass(change) {
  if (change === 'RISE') return 'up'
  if (change === 'FALL') return 'down'
  return 'flat'
}

function formatVolume(vol) {
  if (vol == null) return '-'
  if (vol >= 1_000_000_000_000) return (vol / 1_000_000_000_000).toFixed(1) + '조'
  if (vol >= 100_000_000) return (vol / 100_000_000).toFixed(1) + '억'
  return vol.toLocaleString('ko-KR')
}
</script>

<style scoped>
.compare-page { padding: 1.5rem; max-width: 1100px; margin: 0 auto; }
.page-header { margin-bottom: 1.5rem; }
.page-title { font-size: 1.4rem; font-weight: 700; margin: 0 0 6px; }
.page-desc { color: #6b7280; font-size: 0.9rem; margin: 0; }

.select-section { margin-bottom: 1.5rem; }
.search-input {
  width: 100%; max-width: 360px; padding: 0.5rem 0.875rem;
  border: 1px solid #d1d5db; border-radius: 8px; font-size: 0.9rem;
  outline: none; margin-bottom: 0.75rem;
}

.selected-chips { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 0.75rem; }
.chip {
  display: inline-flex; align-items: center; gap: 6px;
  background: #eff6ff; color: #2563eb;
  padding: 6px 10px 6px 12px; border-radius: 99px; font-size: 0.82rem; font-weight: 600;
}
.chip-remove {
  background: none; border: none; cursor: pointer;
  color: #2563eb; font-size: 0.75rem; padding: 0; line-height: 1;
}

.coin-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 8px; max-height: 280px; overflow-y: auto; padding: 4px;
}
.coin-pick {
  display: flex; flex-direction: column; align-items: flex-start; gap: 2px;
  padding: 8px 12px; border: 1px solid #e5e7eb; border-radius: 8px;
  background: #fff; cursor: pointer; transition: all 0.15s; text-align: left;
}
.coin-pick:hover:not(:disabled) { border-color: #2563eb; }
.coin-pick.active { border-color: #2563eb; background: #eff6ff; }
.coin-pick:disabled { opacity: 0.4; cursor: not-allowed; }
.pick-kor { font-size: 0.85rem; font-weight: 600; }
.pick-sym { font-size: 0.72rem; color: #9ca3af; }

.limit-msg { font-size: 0.82rem; color: #f59e0b; margin-bottom: 1rem; }

.section-title { font-size: 1.05rem; font-weight: 600; margin: 0 0 12px; }
.chart-title { margin-top: 2rem; }

.compare-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.compare-table th {
  text-align: left; padding: 0.5rem 0.75rem;
  border-bottom: 2px solid #e5e7eb; color: #6b7280; font-weight: 500;
}
.compare-table td { padding: 0.6rem 0.75rem; border-bottom: 1px solid #f3f4f6; }
.text-right { text-align: right !important; }
.name-cell { display: flex; flex-direction: column; }
.kor { font-weight: 600; }
.eng { font-size: 0.78rem; color: #9ca3af; }
.up { color: #ef4444; }
.down { color: #3b82f6; }
.flat { color: #6b7280; }

.chart-wrap { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 1rem; }

.loading, .empty-state {
  color: #9ca3af; padding: 3rem 0; text-align: center; font-size: 0.95rem;
}
.result-loading { padding: 4rem 0; }
</style>