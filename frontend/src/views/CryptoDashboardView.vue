<template>
  <div class="dashboard">
    <ToastNotification ref="toastRef" />

    <section v-if="authStore.isLoggedIn" class="favorites-section">
      <h2 class="section-title">⭐ 즐겨찾기</h2>
      <p v-if="cryptoStore.watchlistCoins.length === 0" class="empty-msg">
        즐겨찾기한 코인이 없습니다. 아래 목록에서 별표를 눌러 추가해보세요!
      </p>
      <div v-else class="fav-grid">
        <div v-for="item in cryptoStore.watchlistCoins" :key="item.coin_symbol" class="fav-card" @click="$router.push(`/crypto/${item.market}`)">
          <div class="fav-card-header">
            <span class="coin-kor">{{ item.korean_name }}</span>
            <button class="star-btn active" @click.stop="cryptoStore.toggleWatchlist(item.coin_symbol)">★</button>
          </div>
          <div class="fav-card-market">{{ item.market }}</div>
          <div class="fav-card-price">{{ formatPrice(item.trade_price) }}</div>
          <div class="fav-card-rate" :class="changeClass(item.change)">
            {{ formatRate(item.change_rate, item.change) }}
          </div>
        </div>
      </div>
    </section>

    <hr v-if="authStore.isLoggedIn" class="divider" />

    <div class="toolbar">
      <input v-model="cryptoStore.searchQuery" type="text" placeholder="코인명, 심볼 검색..." class="search-input" />
      <button class="sync-btn" :disabled="isSyncing" @click="handleSync">
        {{ isSyncing ? '동기화 중...' : '🔄 마켓 동기화' }}
      </button>
    </div>

    <section>
      <h2 class="section-title">전체 코인 ({{ cryptoStore.filteredCoins.length }})</h2>
      <div v-if="cryptoStore.isLoading && !cryptoStore.initialLoaded" class="loading">불러오는 중...</div>
      <table v-else class="coin-table">
        <thead>
          <tr>
            <th></th><th>코인명</th><th>마켓</th><th class="text-right">현재가</th><th class="text-right">등락률</th><th>거래대금(24h)</th><th class="text-center">포트폴리오 추가</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="coin in cryptoStore.filteredCoins" :key="coin.market" class="coin-row" @click="$router.push(`/crypto/${coin.market}`)">
            <td>
              <button v-if="authStore.isLoggedIn" class="star-btn" :class="{ active: cryptoStore.watchlistSymbols.has(coin.coin_symbol) }" @click.stop="cryptoStore.toggleWatchlist(coin.coin_symbol)">
                {{ cryptoStore.watchlistSymbols.has(coin.coin_symbol) ? '★' : '☆' }}
              </button>
            </td>
            <td class="name-cell"><span class="kor">{{ coin.korean_name }}</span><span class="eng">{{ coin.english_name }}</span></td>
            <td class="market-code">{{ coin.market }}</td>
            <td class="price">{{ formatPrice(coin.trade_price) }}</td>
            <td class="rate" :class="changeClass(coin.change)">
              {{ formatRate(coin.change_rate, coin.change) }}
            </td>
            <td class="volume">{{ formatVolume(coin.acc_trade_price_24h) }}</td>
            <td class="text-center" @click.stop>
              <div v-if="!authStore.isLoggedIn" class="add-cell">
                <span class="login-required">로그인 필요</span>
              </div>
              <div v-else-if="addTarget?.market !== coin.market" class="add-cell">
                <button
                  class="btn-add-holding"
                  :disabled="coin.trade_price == null"
                  :title="coin.trade_price == null ? '현재가 로딩 중' : ''"
                  @click="openAddInput(coin)"
                >
                  + 추가
                </button>
              </div>
              <div v-else class="add-input-row">
                <input
                  v-model.number="addQuantity"
                  type="number"
                  min="0.00000001"
                  step="0.00000001"
                  placeholder="수량"
                  class="qty-input"
                  @keyup.enter="confirmAddHolding(coin)"
                />
                <button
                  class="btn-confirm"
                  :disabled="!addQuantity || addQuantity <= 0 || isSubmittingAdd"
                  @click="confirmAddHolding(coin)"
                >
                  {{ isSubmittingAdd ? '처리중' : '확인' }}
                </button>
                <button class="btn-cancel-mini" @click="closeAddInput">취소</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCryptoStore } from '@/stores/crypto'
import { useAuthStore } from '@/stores/auth'
import { addCryptoHolding } from '@/api/portfolio'
import ToastNotification from '@/components/crypto/ToastNotification.vue'

const cryptoStore = useCryptoStore()
const authStore = useAuthStore()
const router = useRouter()
const toastRef = ref(null)
const isSyncing = ref(false)

onMounted(async () => {
  cryptoStore.setAlertCallback((toast) => { toastRef.value?.add(toast) })
  await cryptoStore.startPolling()
  if (authStore.isLoggedIn) { await cryptoStore.loadWatchlist() }
})

onUnmounted(() => {
  cryptoStore.stopPolling()
  cryptoStore.setAlertCallback(null)
})

async function handleSync() {
  isSyncing.value = true
  try {
    await cryptoStore.syncMarkets()
    toastRef.value?.add({ type: 'up', name: '동기화 완료', message: `${cryptoStore.coins.length}개 코인 업데이트됨` })
  } finally { isSyncing.value = false }
}

function formatPrice(price) {
  if (price == null) return '-'
  return price >= 100 ? price.toLocaleString('ko-KR') + ' 원' : price.toFixed(4) + ' 원'
}

function formatRate(rate, change) {
  if (change === 'EVEN' || Math.abs(rate) < 0.000001) return '0.00%';
  const sign = (change === 'RISE') ? '+' : '-';
  return sign + (Math.abs(rate) * 100).toFixed(2) + '%';
}

function changeClass(change) {
  if (change === 'RISE') return 'up';
  if (change === 'FALL') return 'down';
  return 'flat';
}

function formatVolume(vol) {
  if (vol == null) return '-'
  if (vol >= 1_000_000_000_000) return (vol / 1_000_000_000_000).toFixed(1) + '조'
  if (vol >= 100_000_000) return (vol / 100_000_000).toFixed(1) + '억'
  return vol.toLocaleString('ko-KR')
}

// ── 포트폴리오에 현재가로 추가 ───────────────────────────
const addTarget = ref(null)
const addQuantity = ref(null)
const isSubmittingAdd = ref(false)

function openAddInput(coin) {
  addTarget.value = coin
  addQuantity.value = null
}

function closeAddInput() {
  addTarget.value = null
  addQuantity.value = null
}

async function confirmAddHolding(coin) {
  if (!addQuantity.value || addQuantity.value <= 0) return

  if (coin.trade_price == null) {
    alert('현재가를 불러오는 중입니다. 잠시 후 다시 시도해주세요.')
    return
  }

  const submittedQuantity = addQuantity.value

  isSubmittingAdd.value = true
  try {
    await addCryptoHolding({
      asset_code: coin.market,
      asset_name: coin.korean_name,
      quantity: submittedQuantity,
      purchase_price: coin.trade_price,
    })
    closeAddInput()
    alert(`${coin.korean_name} ${submittedQuantity}개가 포트폴리오에 추가되었습니다.`)
    router.push({ name: 'mypage', query: { tab: 'portfolio' } })
  } catch (error) {
    console.error('포트폴리오 추가 실패:', error)
    alert('포트폴리오 추가에 실패했습니다.')
  } finally {
    isSubmittingAdd.value = false
  }
}
</script>

<style scoped>
.dashboard { padding: 1.5rem; max-width: 1200px; margin: 0 auto; }
.section-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 0.75rem; }
.divider { border: none; border-top: 1px solid #e5e7eb; margin: 1.5rem 0; }
.fav-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 0.75rem; margin-bottom: 1rem; }
.fav-card { border: 1px solid #e5e7eb; border-radius: 10px; padding: 0.875rem; cursor: pointer; transition: box-shadow 0.15s; }
.fav-card:hover { box-shadow: 0 2px 10px rgba(0,0,0,0.08); }
.fav-card-header { display: flex; justify-content: space-between; align-items: center; }
.coin-kor { font-weight: 600; font-size: 0.95rem; }
.fav-card-market { font-size: 0.72rem; color: #9ca3af; margin-top: 0.2rem; }
.fav-card-price { font-size: 1rem; font-weight: 600; margin-top: 0.5rem; }
.fav-card-rate { font-size: 0.85rem; margin-top: 0.15rem; }
.toolbar { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; }
.search-input { flex: 1; max-width: 360px; padding: 0.5rem 0.875rem; border: 1px solid #d1d5db; border-radius: 8px; font-size: 0.9rem; outline: none; }
.sync-btn { padding: 0.5rem 1rem; border: 1px solid #d1d5db; border-radius: 8px; background: white; font-size: 0.85rem; cursor: pointer; }
.coin-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.coin-table th { text-align: left; padding: 0.5rem 0.75rem; border-bottom: 2px solid #e5e7eb; color: #6b7280; }
.coin-row { cursor: pointer; }
.coin-row:hover { background: #f9fafb; }
.coin-row td { padding: 0.5rem 0.75rem; border-bottom: 1px solid #f3f4f6; }
.up { color: #ef4444; }
.down { color: #3b82f6; }
.flat { color: #6b7280; }
.star-btn { background: none; border: none; cursor: pointer; font-size: 1.1rem; color: #d1d5db; padding: 0; }
.star-btn.active { color: #f59e0b; }

/* ── 정렬 헬퍼 ── */
.text-right { text-align: right !important; }
.text-center { text-align: center !important; }

/* ── 포트폴리오 추가 UI (StockWatchlistView와 동일 패턴) ── */
.add-cell { display: flex; justify-content: center; }
.login-required { font-size: 0.75rem; color: #9ca3af; }
.btn-add-holding {
  padding: 4px 12px;
  border: 1px solid #2563eb;
  border-radius: 6px;
  background: #fff;
  color: #2563eb;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s;
}
.btn-add-holding:hover { background: #2563eb; color: #fff; }
.btn-add-holding:disabled {
  border-color: #d1d5db;
  color: #9ca3af;
  cursor: not-allowed;
}
.btn-add-holding:disabled:hover { background: #fff; color: #9ca3af; }

.add-input-row { display: flex; align-items: center; gap: 4px; justify-content: center; }
.qty-input { width: 72px; padding: 4px 6px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 0.8rem; }
.btn-confirm { padding: 4px 8px; border: none; border-radius: 6px; background: #2563eb; color: #fff; font-size: 0.75rem; cursor: pointer; white-space: nowrap; }
.btn-confirm:disabled { background: #aaa; cursor: not-allowed; }
.btn-cancel-mini { padding: 4px 8px; border: none; border-radius: 6px; background: #f1f5f9; color: #64748b; font-size: 0.75rem; cursor: pointer; }
</style>