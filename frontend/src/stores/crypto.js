// frontend/src/stores/crypto.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { cryptoAPI } from '@/api/crypto'

export const useCryptoStore = defineStore('crypto', () => {

  // ── State ─────────────────────────────────────────────────
  const coins = ref([])
  const watchlist = ref([])
  const searchQuery = ref('')
  const isLoading = ref(false)
  const initialLoaded = ref(false)

  // ── 변동률 알림 콜백 ──────────────────────────────────────
  let alertCallback = null

  function setAlertCallback(fn) {
    alertCallback = fn
  }

  // ── Computed ──────────────────────────────────────────────
  const watchlistSymbols = computed(() =>
    new Set(watchlist.value.map(w => w.coin_symbol))
  )

  const filteredCoins = computed(() => {
    const q = searchQuery.value.trim().toLowerCase()
    if (!q) return coins.value
    return coins.value.filter(c =>
      c.korean_name.toLowerCase().includes(q) ||
      c.english_name.toLowerCase().includes(q) ||
      c.market.toLowerCase().includes(q)
    )
  })

  const watchlistCoins = computed(() => watchlist.value)

  // ── Actions ───────────────────────────────────────────────
  async function loadCoins() {
    if (!initialLoaded.value) isLoading.value = true

    try {
      const { data } = await cryptoAPI.getCoins()

      if (!initialLoaded.value) {
        coins.value = data
        initialLoaded.value = true
      } else {
        const map = new Map(data.map(c => [c.market, c]))
        coins.value.forEach(coin => {
          const fresh = map.get(coin.market)
          if (!fresh) return

          // ── 변동률 알림 체크 (±5% 초과) ──────────────────
          const oldRate = coin.change_rate ?? 0
          const newRate = fresh.change_rate ?? 0
          if (alertCallback && Math.abs(newRate) >= 0.05) {
            if (Math.abs(newRate) > Math.abs(oldRate) + 0.001) {
              alertCallback({
                type: newRate > 0 ? 'up' : 'down',
                name: coin.korean_name,
                message: `${(newRate * 100).toFixed(2)}% ${newRate > 0 ? '급등' : '급락'}`,
              })
            }
          }

          coin.trade_price          = fresh.trade_price
          coin.change               = fresh.change
          coin.change_rate          = fresh.change_rate
          coin.change_price         = fresh.change_price
          coin.acc_trade_price_24h  = fresh.acc_trade_price_24h
          coin.acc_trade_volume_24h = fresh.acc_trade_volume_24h
          coin.high_price           = fresh.high_price
          coin.low_price            = fresh.low_price
          coin.is_favorite          = fresh.is_favorite
        })
      }
    } finally {
      isLoading.value = false
    }
  }

  async function loadWatchlist() {
    const { data } = await cryptoAPI.getFavorites()
    watchlist.value = data
  }

  async function toggleWatchlist(coinSymbol) {
    if (watchlistSymbols.value.has(coinSymbol)) {
      await cryptoAPI.removeFavorite(coinSymbol)
    } else {
      await cryptoAPI.addFavorite(coinSymbol)
    }
    await loadWatchlist()
  }

  async function syncMarkets() {
    await cryptoAPI.syncMarkets()
    // 캐시 초기화 후 새 데이터 강제 로드
    initialLoaded.value = false
    await loadCoins()
  }

  // ── Upbit 실시간 폴링 (10초) ──────────────────────────────
  let pollingTimer = null

  async function startPolling() {
    await loadCoins()
    pollingTimer = setInterval(loadCoins, 10_000)
  }

  function stopPolling() {
    clearInterval(pollingTimer)
    pollingTimer = null
  }

  return {
    coins,
    watchlist,
    searchQuery,
    isLoading,
    initialLoaded,
    watchlistSymbols,
    filteredCoins,
    watchlistCoins,
    setAlertCallback,
    loadCoins,
    loadWatchlist,
    toggleWatchlist,
    syncMarkets,
    startPolling,
    stopPolling,
  }
})