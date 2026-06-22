// src/stores/watchlist.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getWatchlist,
  addWatchlist,
  removeWatchlist,
  upsertPortfolio,
  getStockDashboard,   // 대시보드용 추가
} from '@/api/stocks'

export const useWatchlistStore = defineStore('watchlist', () => {

  // ── 상태 ─────────────────────────────────────────────
  const items        = ref([])    // 관심 종목 목록 (대시보드 데이터 포함)
  const isLoading    = ref(false)
  const initialLoaded = ref(false) // 첫 로드 완료 여부 (크립토와 동일한 패턴)
  const error        = ref(null)
  const searchQuery  = ref('')     // 검색 필터

  // ── Computed ─────────────────────────────────────────
  const watchedSymbols = computed(() =>
    items.value.map(item => item.symbol)
  )

  // 검색어 필터링 (크립토와 동일한 패턴)
  const filteredItems = computed(() => {
    const q = searchQuery.value.trim().toLowerCase()
    if (!q) return items.value
    return items.value.filter(item =>
      item.symbol.toLowerCase().includes(q) ||
      item.name.toLowerCase().includes(q) ||
      item.market.toLowerCase().includes(q)
    )
  })

  // 포트폴리오가 입력된 종목만
  const portfolioItems = computed(() =>
    items.value.filter(item => item.average_price != null)
  )

  // ── 대시보드 데이터 로드 (폴링용) ────────────────────
  // 크립토의 loadCoins()와 동일한 역할
  async function loadDashboard() {
    // 첫 로드가 아니면 로딩 스피너 없이 조용히 갱신 (크립토와 동일)
    if (!initialLoaded.value) isLoading.value = true

    try {
      const res = await getStockDashboard()

      if (!initialLoaded.value) {
        // 첫 로드: 전체 교체
        items.value = res.data
        initialLoaded.value = true
      } else {
        // 이후 폴링: 현재가/수익률만 부드럽게 업데이트 (깜빡임 방지)
        const map = new Map(res.data.map(d => [d.id, d]))
        items.value.forEach(item => {
          const fresh = map.get(item.id)
          if (!fresh) return
          item.current_price = fresh.current_price
          item.profit_rate   = fresh.profit_rate
        })
      }
    } catch (err) {
      error.value = '데이터를 불러오지 못했습니다.'
    } finally {
      isLoading.value = false
    }
  }

  // ── 10초 폴링 (크립토와 동일한 패턴) ─────────────────
  let pollingTimer = null

  async function startPolling() {
    await loadDashboard()
    pollingTimer = setInterval(loadDashboard, 10_000)
  }

  function stopPolling() {
    clearInterval(pollingTimer)
    pollingTimer = null
  }

  // ── 기존 액션들 ───────────────────────────────────────
  async function fetchWatchlist() {
    isLoading.value = true
    error.value = null
    try {
      const res = await getWatchlist()
      items.value = res.data
      initialLoaded.value = true
    } catch (err) {
      error.value = '관심 종목을 불러오는 데 실패했습니다.'
    } finally {
      isLoading.value = false
    }
  }

  async function addToWatchlist(stockInfo) {
    try {
      const res = await addWatchlist(stockInfo)
      items.value.unshift(res.data)
      return { success: true }
    } catch (err) {
      if (err.response?.status === 400) {
        return { success: false, message: '이미 관심 종목에 추가된 종목입니다.' }
      }
      return { success: false, message: '추가에 실패했습니다.' }
    }
  }

  async function removeFromWatchlist(id) {
    try {
      await removeWatchlist(id)
      items.value = items.value.filter(item => item.id !== id)
      return { success: true }
    } catch (err) {
      return { success: false, message: '삭제에 실패했습니다.' }
    }
  }

  async function savePortfolio(watchlistId, portfolioData) {
    try {
      const res = await upsertPortfolio(watchlistId, portfolioData)
      const target = items.value.find(item => item.id === watchlistId)
      if (target) {
        target.portfolio     = res.data
        target.average_price = res.data.average_price
        target.quantity      = res.data.quantity
      }
      return { success: true }
    } catch (err) {
      return { success: false, message: '포트폴리오 저장에 실패했습니다.' }
    }
  }

  return {
    items, isLoading, initialLoaded, error, searchQuery,
    watchedSymbols, filteredItems, portfolioItems,
    loadDashboard, startPolling, stopPolling,
    fetchWatchlist, addToWatchlist, removeFromWatchlist, savePortfolio,
  }
})