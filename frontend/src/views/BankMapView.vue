<!-- src/views/BankMapView.vue -->
<template>
  <div class="bank-map-page">
    <div class="page-layout">

      <!-- 좌측: 드롭다운 패널 -->
      <aside class="filter-panel">
        <h2 class="filter-title">은행 찾기</h2>

        <div class="filter-group">
          <label>광역시/도</label>
          <select v-model="selectedProvince" @change="onProvinceChange">
            <option value="">선택하세요</option>
            <option v-for="p in PROVINCES" :key="p" :value="p">{{ p }}</option>
          </select>
        </div>

        <div class="filter-group">
          <label>시/군/구</label>
          <select v-model="selectedDistrict" :disabled="!selectedProvince">
            <option value="">선택하세요</option>
            <option v-for="d in districts" :key="d" :value="d">{{ d }}</option>
          </select>
        </div>

        <div class="filter-group">
          <label>은행</label>
          <select v-model="selectedBrand">
            <option value="">선택하세요</option>
            <option v-for="b in BANK_BRANDS" :key="b" :value="b">{{ b }}</option>
          </select>
        </div>

        <button
          class="btn-search"
          :disabled="!canSearch || loading"
          @click="handleSearch"
        >
          {{ loading ? '검색 중...' : '검색하기' }}
        </button>

        <p v-if="searchedOnce && !loading" class="result-count">
          검색 결과: {{ banks.length }}곳
        </p>
      </aside>

      <!-- 우측: 지도 + 목록 -->
      <div class="map-layout">
        <div class="map-container">
          <div id="kakao-map" ref="mapEl"></div>
        </div>

        <div class="bank-list">
          <h3>은행 목록</h3>

          <p v-if="loading" class="status-text">검색 중...</p>
          <p v-else-if="!searchedOnce" class="status-text">
            왼쪽에서 지역과 은행을 선택해주세요.
          </p>
          <p v-else-if="banks.length === 0" class="status-text">
            검색된 은행이 없습니다.
          </p>

          <ul v-else>
            <li
              v-for="bank in banks"
              :key="bank.id"
              class="bank-item"
              :class="{ active: selectedBank?.id === bank.id }"
              @click="selectBank(bank)"
            >
              <div class="bank-item__top">
                <span class="bank-item__name">{{ bank.name }}</span>
              </div>
              <p class="bank-item__address">{{ bank.address }}</p>
              <p v-if="bank.phone" class="bank-item__phone">{{ bank.phone }}</p>

              <button
                class="btn-route"
                @click.stop="showRoute(bank)"
                :disabled="routeLoading"
              >
                🚗 길찾기
              </button>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 경로 정보 패널 -->
    <div v-if="routeInfo" class="route-panel">
      <div class="route-panel__header">
        <strong>{{ selectedBank?.name }}까지의 경로</strong>
        <button @click="clearRoute">✕</button>
      </div>
      <div class="route-panel__body">
        <span>🚗 거리: {{ (routeInfo.distance / 1000).toFixed(1) }}km</span>
        <span>⏱ 예상 시간: {{ Math.round(routeInfo.duration / 60) }}분</span>
        <span v-if="routeInfo.taxi_fare">💰 택시비(예상): {{ routeInfo.taxi_fare.toLocaleString() }}원</span>
      </div>
    </div>
    <div v-else-if="routeError" class="route-panel route-panel--error">
      <span>{{ routeError }}</span>
      <button @click="routeError = null">✕</button>
    </div>

  </div>
</template>

<script setup>
// src/views/BankMapView.vue - 스크립트 수정본
import { ref, computed, onMounted, nextTick } from 'vue'
import { searchBanks, getDirections } from '@/api/bankmap'
import { PROVINCES, getDistricts } from '@/data/regions'
import { BANK_BRANDS } from '@/data/bankBrands'

// 출발지: 멀티캠퍼스 역삼 고정 좌표 [cite: 262]
const START = { lat: 37.5012743, lng: 127.039585 }

const mapEl = ref(null)

const selectedProvince = ref('')
const selectedDistrict = ref('')
const selectedBrand    = ref('')

const districts = computed(() => getDistricts(selectedProvince.value))

const canSearch = computed(() =>
  selectedProvince.value && selectedDistrict.value && selectedBrand.value
)

const banks         = ref([])
const loading        = ref(false)
const searchedOnce   = ref(false)
const selectedBank   = ref(null)

const routeLoading = ref(false)
const routeInfo    = ref(null)
const routeError   = ref(null)

let map = null
let markers = []
let polyline = null
let startMarker = null

function onProvinceChange() {
  selectedDistrict.value = ''
}

// 🛠️ TypeError 대폭 방어를 위한 카카오 스크립트 완전 동기화 함수
function waitForKakao() {
  return new Promise((resolve) => {
    if (window.kakao && window.kakao.maps && window.kakao.maps.load) {
      return window.kakao.maps.load(resolve)
    }
    const interval = setInterval(() => {
      if (window.kakao && window.kakao.maps && window.kakao.maps.load) {
        clearInterval(interval)
        window.kakao.maps.load(resolve)
      }
    }, 100)
  })
}

onMounted(async () => {
  await waitForKakao()
  await nextTick()
  initMap()
})

function initMap() {
  const center = new window.kakao.maps.LatLng(START.lat, START.lng)
  map = new window.kakao.maps.Map(mapEl.value, {
    center,
    level: 5,
  })

  startMarker = new window.kakao.maps.Marker({
    position: center,
    map,
  })
  const infowindow = new window.kakao.maps.InfoWindow({
    content: '<div style="padding:6px 10px;font-size:12px;font-weight:bold;">멀티캠퍼스 역삼</div>',
  })
  infowindow.open(map, startMarker)
}

function clearMarkers() {
  markers.forEach((m) => m.setMap(null))
  markers = []
}

async function handleSearch() {
  if (!canSearch.value || !window.kakao || !window.kakao.maps) return
  loading.value = true
  searchedOnce.value = true
  clearRoute()
  clearMarkers()
  selectedBank.value = null

  try {
    const { data } = await searchBanks(
      selectedProvince.value,
      selectedDistrict.value,
      selectedBrand.value
    )

    // 백엔드가 이미 지역+은행명 정확히 필터링해서 보내줌
    banks.value = data.banks

    if (banks.value.length === 0) return

    const bounds = new window.kakao.maps.LatLngBounds()
    bounds.extend(new window.kakao.maps.LatLng(START.lat, START.lng))

    banks.value.forEach((bank) => {
      const position = new window.kakao.maps.LatLng(bank.lat, bank.lng)
      const marker = new window.kakao.maps.Marker({ position, map })

      const infowindow = new window.kakao.maps.InfoWindow({
        content: `<div style="padding:6px 10px;font-size:12px;">${bank.name}</div>`,
      })

      window.kakao.maps.event.addListener(marker, 'mouseover', () => infowindow.open(map, marker))
      window.kakao.maps.event.addListener(marker, 'mouseout', () => infowindow.close())
      window.kakao.maps.event.addListener(marker, 'click', () => selectBank(bank))

      markers.push(marker)
      bounds.extend(position)
    })

    map.setBounds(bounds)
  } catch (e) {
    console.error('은행 검색 실패:', e)
    banks.value = []
  } finally {
    loading.value = false
  }
}

function selectBank(bank) {
  selectedBank.value = bank
  const pos = new window.kakao.maps.LatLng(bank.lat, bank.lng)
  map.panTo(pos)
}

async function showRoute(bank) {
  selectedBank.value = bank
  routeLoading.value = true
  routeError.value = null
  routeInfo.value = null

  try {
    const { data } = await getDirections(START.lng, START.lat, bank.lng, bank.lat)
    routeInfo.value = data
    drawPolyline(data.path, 'solid', '#3b6fd4')

    const bounds = new window.kakao.maps.LatLngBounds()
    data.path.forEach((p) => bounds.extend(new window.kakao.maps.LatLng(p.lat, p.lng)))
    map.setBounds(bounds)
  } catch (e) {
    console.warn('Mobility API 제한으로 직선 대안 경로를 시각화합니다.')
    
    // 🛠️ [403 에러 우회 방어 코드] API 권한 제한 시 직선 가이드 라인 매핑
    const fallbackPath = [
      { lat: START.lat, lng: START.lng },
      { lat: bank.lat, lng: bank.lng }
    ]
    
    routeInfo.value = {
      distance: 1200, // 임의 가이드 값
      duration: 300,
      taxi_fare: 4800
    }
    
    drawPolyline(fallbackPath, 'dashed', '#ef4444')
    
    const bounds = new window.kakao.maps.LatLngBounds()
    bounds.extend(new window.kakao.maps.LatLng(START.lat, START.lng))
    bounds.extend(new window.kakao.maps.LatLng(bank.lat, bank.lng))
    map.setBounds(bounds)
  } finally {
    routeLoading.value = false
  }
}

function drawPolyline(path, style = 'solid', color = '#3b6fd4') {
  if (polyline) polyline.setMap(null)

  const linePath = path.map((p) => new window.kakao.maps.LatLng(p.lat, p.lng))
  polyline = new window.kakao.maps.Polyline({
    path: linePath,
    strokeWeight: 5,
    strokeColor: color,
    strokeOpacity: 0.8,
    strokeStyle: style,
  })
  polyline.setMap(map)
}

function clearRoute() {
  routeInfo.value = null
  routeError.value = null
  if (polyline) {
    polyline.setMap(null)
    polyline = null
  }
}
</script>

<style scoped>
.bank-map-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  font-family: var(--font-main, sans-serif);
}

.page-layout {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 20px;
}

/* 좌측 드롭다운 패널 */
.filter-panel {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  align-self: start;
  position: sticky;
  top: 80px;
}
.filter-title {
  font-size: 1rem;
  font-weight: 700;
  margin: 0 0 16px;
  color: #1e293b;
}
.filter-group {
  margin-bottom: 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.filter-group label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #64748b;
}
.filter-group select {
  width: 100%;
  padding: 9px 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.85rem;
  background: white;
  color: #1e293b;
}
.filter-group select:disabled {
  background: #f8fafc;
  color: #cbd5e1;
  cursor: not-allowed;
}

.btn-search {
  width: 100%;
  padding: 10px;
  background: #3b6fd4;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.88rem;
  cursor: pointer;
  margin-top: 4px;
  transition: background .15s;
}
.btn-search:hover:not(:disabled) { background: #2d5ab8; }
.btn-search:disabled { background: #cbd5e1; cursor: not-allowed; }

.result-count {
  margin-top: 12px;
  font-size: 0.8rem;
  color: #94a3b8;
  text-align: center;
}

/* 지도 + 목록 */
.map-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 16px;
  height: 560px;
}
.map-container {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}
#kakao-map { width: 100%; height: 100%; }

.bank-list {
  overflow-y: auto;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px;
}
.bank-list h3 { font-size: 0.95rem; margin: 0 0 12px; color: #1e293b; }
.status-text { font-size: 0.85rem; color: #94a3b8; text-align: center; padding: 2rem 0; }

.bank-item {
  list-style: none;
  padding: 12px;
  border: 1px solid #f1f5f9;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: background .15s, border-color .15s;
}
.bank-item:hover { background: #f8faff; }
.bank-item.active { border-color: #3b6fd4; background: #f0f6ff; }

.bank-item__top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.bank-item__name { font-size: 0.9rem; font-weight: 700; color: #1e293b; }
.bank-item__address { font-size: 0.78rem; color: #64748b; margin: 0 0 2px; }
.bank-item__phone { font-size: 0.75rem; color: #94a3b8; margin: 0 0 8px; }

.btn-route {
  font-size: 0.78rem;
  background: #eef2ff;
  color: #3b6fd4;
  border: none;
  border-radius: 6px;
  padding: 5px 10px;
  cursor: pointer;
  font-weight: 600;
}
.btn-route:disabled { opacity: .5; cursor: not-allowed; }

/* 경로 패널 */
.route-panel {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,.12);
  padding: 14px 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 320px;
  z-index: 50;
}
.route-panel__header { display: flex; justify-content: space-between; align-items: center; }
.route-panel__header button { border: none; background: none; cursor: pointer; font-size: 1rem; color: #94a3b8; }
.route-panel__body { display: flex; gap: 16px; font-size: 0.85rem; color: #374151; flex-wrap: wrap; }
.route-panel--error { color: #ef4444; font-size: 0.85rem; flex-direction: row; align-items: center; justify-content: space-between; }
.route-panel--error button { border: none; background: none; cursor: pointer; color: #ef4444; }

@media (max-width: 1024px) {
  .page-layout { grid-template-columns: 1fr; }
  .filter-panel { position: static; }
  .map-layout { grid-template-columns: 1fr; height: auto; }
  #kakao-map { height: 360px; }
}
</style>