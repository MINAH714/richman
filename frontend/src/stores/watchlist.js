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
  const activeTab      = ref('kr')
  const dashboardItems = ref([])
  const isRefreshing   = ref(false)
  const hasMore        = ref(false)   // 더보기 가능 여부
  const currentOffset  = ref(0)       // 현재까지 로드된 개수
  const isLoadingMore  = ref(false)   // 더보기 로딩 중 여부
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
  if (!initialLoaded.value) isLoading.value = true

  try {
    // 항상 offset=0으로 첫 30개 새로 조회 (폴링용)
    const res = await getStockDashboard(activeTab.value, 0, 30)
    const { stocks, has_more } = res.data

    if (!initialLoaded.value) {
      dashboardItems.value = stocks
      initialLoaded.value  = true
    } else {
      // 갱신 시 깜빡임 트리거
      isRefreshing.value = true
      setTimeout(() => { isRefreshing.value = false }, 200)

      // 현재가/등락률만 업데이트 (이미 더보기로 로드된 항목 포함)
      const map = new Map(stocks.map(d => [d.symbol, d]))
      dashboardItems.value.forEach(item => {
        const fresh = map.get(item.symbol)
        if (!fresh) return
        item.current_price = fresh.current_price
        item.change_rate   = fresh.change_rate
        item.change_type   = fresh.change_type
        item.is_watched    = fresh.is_watched
      })
    }

    // 더보기 상태 업데이트
    // 현재 로드된 개수가 30개 초과면 has_more는 서버 응답 기준
    hasMore.value       = has_more
    currentOffset.value = dashboardItems.value.length

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

  // 탭 변경 시 데이터 새로 로드
  async function changeTab(tab) {
    activeTab.value      = tab
    initialLoaded.value  = false   // 탭 바뀌면 첫 로드처럼 처리
    dashboardItems.value = []
    await loadDashboard()
  }

  async function toggleWatchlist(stockInfo) {
  const already = items.value.find(i => i.symbol === stockInfo.symbol)
  if (already) {
    await removeFromWatchlist(already.id)
  } else {
    await addToWatchlist({
      symbol: stockInfo.symbol,
      name:   stockInfo.name,
      market: stockInfo.market,
    })
  }
  // 대시보드 is_watched 상태 즉시 반영
  const target = dashboardItems.value.find(i => i.symbol === stockInfo.symbol)
  if (target) target.is_watched = !already
}

  // 더보기 버튼 클릭 시 추가 종목 로드
  async function loadMore() {
    if (isLoadingMore.value || !hasMore.value) return
    isLoadingMore.value = true

    try {
      const res = await getStockDashboard(
        activeTab.value,
        currentOffset.value,  // 현재까지 로드된 수 이후부터
        25                     // 추가 25개씩
      )
      const { stocks, has_more } = res.data

      // 관심 종목 여부 반영 후 기존 목록에 추가
      dashboardItems.value.push(...stocks)
      hasMore.value       = has_more
      currentOffset.value = dashboardItems.value.length

    } catch (err) {
      error.value = '추가 데이터를 불러오지 못했습니다.'
    } finally {
      isLoadingMore.value = false
    }
  }

  return {
    activeTab, dashboardItems, isRefreshing,
    hasMore, currentOffset, isLoadingMore,
    items, isLoading, initialLoaded, error, searchQuery,
    watchedSymbols, filteredItems, portfolioItems,
    loadDashboard, startPolling, stopPolling, changeTab, toggleWatchlist,
    fetchWatchlist, addToWatchlist, removeFromWatchlist, savePortfolio, loadMore,
  }
})