// src/stores/watchlist.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getWatchlist, addWatchlist, removeWatchlist, upsertPortfolio } from '@/api/stocks'

export const useWatchlistStore = defineStore('watchlist', () => {

  // ── 상태(state) ──────────────────────────────────────
  const items = ref([])          // 관심 종목 목록
  const isLoading = ref(false)   // 로딩 중 여부
  const error = ref(null)        // 에러 메시지

  // ── 계산된 값(computed) ──────────────────────────────
  // 관심 종목에 등록된 symbol 목록 (중복 추가 방지용)
  const watchedSymbols = computed(() =>
    items.value.map(item => item.symbol)
  )

  // 포트폴리오가 입력된 종목만 필터링
  const portfolioItems = computed(() =>
    items.value.filter(item => item.portfolio)
  )

  // ── 액션(action) ────────────────────────────────────

  // 관심 종목 목록 불러오기
  async function fetchWatchlist() {
    isLoading.value = true
    error.value = null
    try {
      const res = await getWatchlist()
      items.value = res.data
    } catch (err) {
      error.value = '관심 종목을 불러오는 데 실패했습니다.'
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  // 관심 종목 추가
  // stockInfo 예시: { symbol: 'AAPL', name: 'Apple Inc.', market: 'NASDAQ' }
  async function addToWatchlist(stockInfo) {
    try {
      const res = await addWatchlist(stockInfo)
      // 서버 응답(추가된 항목)을 목록 맨 앞에 추가
      items.value.unshift(res.data)
      return { success: true }
    } catch (err) {
      // 409: 이미 추가된 종목일 경우
      if (err.response?.status === 409 || err.response?.data) {
        return { success: false, message: '이미 관심 종목에 추가된 종목입니다.' }
      }
      return { success: false, message: '추가에 실패했습니다.' }
    }
  }

  // 관심 종목 삭제
  async function removeFromWatchlist(id) {
    try {
      await removeWatchlist(id)
      // 로컬 목록에서도 제거 (서버 재요청 없이 즉시 반영)
      items.value = items.value.filter(item => item.id !== id)
      return { success: true }
    } catch (err) {
      return { success: false, message: '삭제에 실패했습니다.' }
    }
  }

  // 포트폴리오 등록/수정
  // watchlistId: Watchlist pk, portfolioData: { quantity, average_price }
  async function savePortfolio(watchlistId, portfolioData) {
    try {
      const res = await upsertPortfolio(watchlistId, portfolioData)
      // 로컬 목록에서 해당 항목의 portfolio 정보 업데이트
      const target = items.value.find(item => item.id === watchlistId)
      if (target) {
        target.portfolio = res.data
      }
      return { success: true }
    } catch (err) {
      return { success: false, message: '포트폴리오 저장에 실패했습니다.' }
    }
  }

  return {
    items, isLoading, error,
    watchedSymbols, portfolioItems,
    fetchWatchlist, addToWatchlist, removeFromWatchlist, savePortfolio,
  }
})