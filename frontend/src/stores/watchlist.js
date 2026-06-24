// src/stores/watchlist.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getWatchlist,
  addWatchlist,
  removeWatchlist,
  upsertPortfolio,
  getStockDashboard,
  addStockHolding, //마이페이지 포트폴리오 연동용
  getStockPrice, 
} from '@/api/stocks'

export const useWatchlistStore = defineStore('watchlist', () => {
  // ── 상태 ─────────────────────────────────────────────
  const items = ref([])            // 관심 종목 목록
  const activeTab = ref('kr')       // 'kr' | 'us'
  const dashboardItems = ref([])   // 대시보드 종목 목록
  const dashboardLoaded = ref(false) // 대시보드 데이터 로드 완료 여부
  const isRefreshing = ref(false)   // 갱신 깜빡임 애니메이션 트리거
  const hasMore = ref(false)        // 더보기 가능 여부
  const currentOffset = ref(0)       // 현재까지 로드된 개수
  const isLoadingMore = ref(false)   // 더보기 로딩 중 여부
  const isLoading = ref(false)       // 첫 진입 메인 로딩 바용
  const initialLoaded = ref(false)   // 관심종목 첫 로드 완료 여부
  const error = ref(null)
  const searchQuery = ref('')        // 검색 필터

  // ── Computed ─────────────────────────────────────────
  const watchedSymbols = computed(() =>
    items.value.map(item => item.symbol)
  )

  // 검색어 필터링
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

  // ── 헬퍼 함수: 백엔드-프론트엔드 데이터 키 명세 맞춤 정규화 ──
  function normalizeStocks(stocksArray) {
    if (!Array.isArray(stocksArray)) return []
    return stocksArray.map(s => ({
      ...s,
      // 백엔드가 price 혹은 current_price 중 어떤 것을 주더라도 s.price로 일관되게 바인딩
      price: s.price !== undefined ? s.price : s.current_price,
      change: s.change !== undefined ? s.change : s.change_price,
      change_rate: s.change_rate !== undefined ? s.change_rate : s.change_rate
    }))
  }


  // ── 대시보드 데이터 로드 (폴링 및 첫 진입 공용) ──
  async function loadDashboard() {
    if (!dashboardLoaded.value) isLoading.value = true

    try {
      const res = await getStockDashboard(activeTab.value, 0, 30)
      const { stocks, has_more } = res.data

      const normalized = normalizeStocks(stocks)

      if (!dashboardLoaded.value) {
        dashboardItems.value = normalized
        dashboardLoaded.value = true
      } else {
        isRefreshing.value = true
        setTimeout(() => { isRefreshing.value = false }, 200)

        const freshMap = new Map(normalized.map(s => [s.symbol, s]))
        
        dashboardItems.value.forEach(item => {
          const fresh = freshMap.get(item.symbol)
          if (!fresh) return
          item.price = fresh.price
          item.change = fresh.change
          item.change_rate = fresh.change_rate
          item.is_watched = fresh.is_watched
        })
      }

      // 💡 [여기서부터 추가] 상단 관심 종목 카드도 대시보드 가격 데이터를 기반으로 실시간 맵핑
      if (items.value.length > 0 && normalized.length > 0) {
        // 전체 대시보드 주식 정보를 Map으로 변환
        const priceMap = new Map(normalized.map(s => [s.symbol, s]))
        
        items.value.forEach(favItem => {
          const matchedStock = priceMap.get(favItem.symbol)
          if (matchedStock) {
            // 관심 종목 데이터 객체에 실시간 가격 정보 주입
            favItem.price = matchedStock.price
            
            // 만약 유저가 입력한 매수 평균가(average_price)가 포트폴리오에 있다면 수익률 계산
            if (favItem.average_price) {
              const profit = ((matchedStock.price - favItem.average_price) / favItem.average_price) * 100
              favItem.profit_rate = parseFloat(profit.toFixed(2))
            }
          }
        })
      }

      hasMore.value = has_more
      currentOffset.value = dashboardItems.value.length

    } catch (err) {
      error.value = '대시보드 데이터를 불러오지 못했습니다.'
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  // ── 10초 폴링 ──
  let pollingTimer = null

  async function startPolling() {
    if (pollingTimer) return 
    await loadDashboard()
    pollingTimer = setInterval(loadDashboard, 10_000)
  }

  function stopPolling() {
    if (pollingTimer) {
      clearInterval(pollingTimer)
      pollingTimer = null
    }
  }

  // ── 관심종목 및 포트폴리오 CRUD 액션 ──────────────────
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
        target.portfolio = res.data
        target.average_price = res.data.average_price
        target.quantity = res.data.quantity
      }
      return { success: true }
    } catch (err) {
      return { success: false, message: '포트폴리오 저장에 실패했습니다.' }
    }
  }

  // 탭 변경 시 초기화
  async function changeTab(tab) {
    activeTab.value = tab
    dashboardLoaded.value = false
    dashboardItems.value = []
    currentOffset.value = 0
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
        market: stockInfo.market || 'KRX',
      })
    }
    const target = dashboardItems.value.find(i => i.symbol === stockInfo.symbol)
    if (target) target.is_watched = !already
  }
// ⭐ [신규 추가] 대시보드에서 수량을 입력해 관심종목 등록 + 마이페이지 포트폴리오 등록을 한 번에 처리
  // item: 대시보드 종목 객체 (symbol, name, market, price 포함)
  // quantity: 사용자가 입력한 구매 개수
  // 기존 addHoldingWithQuantity 함수 전체를 아래로 교체

  async function addHoldingWithQuantity(item, quantity) {
    try {
      // ① 아직 관심종목에 없다면 관심종목으로도 등록 (기존 stocks 앱 Watchlist)
      const alreadyWatched = items.value.find(i => i.symbol === item.symbol)
      if (!alreadyWatched) {
        await addToWatchlist({
          symbol: item.symbol,
          name:   item.name,
          market: item.market || 'KRX',
        })
        const target = dashboardItems.value.find(i => i.symbol === item.symbol)
        if (target) target.is_watched = true
      }

      // ⭐ [신규 추가] 국내(KRX)가 아니면 환율을 조회해서 원화로 환산
      const isDomestic = (item.market || 'KRX') === 'KRX'
      let purchasePriceKRW = item.price   // 기본값: 국내 주식은 그대로 사용

      if (!isDomestic) {
        const fxRes = await getStockPrice('KRW=X')   // USD/KRW 환율 조회 (HomeView.vue와 동일한 방식)
        const exchangeRate = fxRes.data?.current_price

        if (!exchangeRate) {
          return { success: false, message: '환율 정보를 가져오지 못해 추가에 실패했습니다.' }
        }

        purchasePriceKRW = item.price * exchangeRate   // 달러 단가 → 원화 단가로 환산
      }

      // ② portfolio 앱(UserPortfolio)에 보유 내역 등록 (원화 환산된 단가 기준)
      await addStockHolding({
        asset_code:     item.symbol,
        name:           item.name,
        market:         item.market || 'KRX',
        quantity:       quantity,
        purchase_price: purchasePriceKRW,   // ⭐ [수정] 원화 환산된 단가 전달
      })

      return { success: true }
    } catch (err) {
      console.error(err)
      return { success: false, message: '포트폴리오 추가에 실패했습니다.' }
    }
  }


  // 더보기 버튼 클릭 시 추가 종목 로드
  async function loadMore() {
    if (isLoadingMore.value || !hasMore.value) return
    isLoadingMore.value = true

    try {
      const res = await getStockDashboard(
        activeTab.value,
        currentOffset.value,
        25
      )
      const { stocks, has_more } = res.data

      // 무한 스크롤 조각 데이터도 빠짐없이 규격 정규화 전처리 적용
      const normalized = normalizeStocks(stocks)

      dashboardItems.value.push(...normalized)
      hasMore.value = has_more
      currentOffset.value = dashboardItems.value.length

    } catch (err) {
      error.value = '추가 데이터를 불러오지 못했습니다.'
      console.error(err)
    } finally {
      isLoadingMore.value = false
    }
  }

  return {
    activeTab, dashboardItems, isRefreshing,
    hasMore, currentOffset, isLoadingMore,
    items, isLoading, initialLoaded, dashboardLoaded, error, searchQuery,
    watchedSymbols, filteredItems, portfolioItems,
    loadDashboard, startPolling, stopPolling, changeTab, toggleWatchlist,
    fetchWatchlist, addToWatchlist, removeFromWatchlist, savePortfolio, loadMore,
    addHoldingWithQuantity,
  }
})