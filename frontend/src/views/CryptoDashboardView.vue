<!-- frontend/src/views/CryptoDashboardView.vue -->
<template>
  <div class="dashboard">

    <!-- 토스트 알림 -->
    <ToastNotification ref="toastRef" />

    <!-- ── 즐겨찾기 섹션 ───────────────────────────────────── -->
    <section v-if="authStore.isLoggedIn" class="favorites-section">
      <h2 class="section-title">⭐ 즐겨찾기</h2>

      <p v-if="cryptoStore.watchlistCoins.length === 0" class="empty-msg">
        즐겨찾기한 코인이 없습니다. 아래 목록에서 별표를 눌러 추가해보세요!
      </p>

      <div v-else class="fav-grid">
        <div
          v-for="item in cryptoStore.watchlistCoins"
          :key="item.coin_symbol"
          class="fav-card"
          @click="$router.push(`/crypto/${item.market}`)"
        >
          <div class="fav-card-header">
            <span class="coin-kor">{{ item.korean_name }}</span>
            <button
              class="star-btn active"
              @click.stop="cryptoStore.toggleWatchlist(item.coin_symbol)"
            >★</button>
          </div>
          <div class="fav-card-market">{{ item.market }}</div>
          <div class="fav-card-price">{{ formatPrice(item.trade_price) }}</div>
          <div class="fav-card-rate" :class="changeClass(item.change)">
            {{ formatRate(item.change_rate) }}
          </div>
        </div>
      </div>
    </section>

    <hr v-if="authStore.isLoggedIn" class="divider" />

    <!-- ── 검색 바 + 동기화 버튼 ─────────────────────────── -->
    <div class="toolbar">
      <input
        v-model="cryptoStore.searchQuery"
        type="text"
        placeholder="코인명, 심볼 검색..."
        class="search-input"
      />
      <button
        class="sync-btn"
        :disabled="isSyncing"
        @click="handleSync"
      >
        {{ isSyncing ? '동기화 중...' : '🔄 마켓 동기화' }}
      </button>
    </div>

    <!-- ── 전체 코인 테이블 ───────────────────────────────── -->
    <section>
      <h2 class="section-title">
        전체 코인 ({{ cryptoStore.filteredCoins.length }})
      </h2>

      <div v-if="cryptoStore.isLoading && !cryptoStore.initialLoaded" class="loading">
        불러오는 중...
      </div>

      <table v-else class="coin-table">
        <thead>
          <tr>
            <th></th>
            <th>코인명</th>
            <th>마켓</th>
            <th>현재가</th>
            <th>등락률</th>
            <th>거래대금(24h)</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="coin in cryptoStore.filteredCoins"
            :key="coin.market"
            class="coin-row"
            @click="$router.push(`/crypto/${coin.market}`)"
          >
            <td>
              <button
                v-if="authStore.isLoggedIn"
                class="star-btn"
                :class="{ active: cryptoStore.watchlistSymbols.has(coin.coin_symbol) }"
                @click.stop="cryptoStore.toggleWatchlist(coin.coin_symbol)"
              >
                {{ cryptoStore.watchlistSymbols.has(coin.coin_symbol) ? '★' : '☆' }}
              </button>
            </td>
            <td class="name-cell">
              <span class="kor">{{ coin.korean_name }}</span>
              <span class="eng">{{ coin.english_name }}</span>
            </td>
            <td class="market-code">{{ coin.market }}</td>
            <td class="price">{{ formatPrice(coin.trade_price) }}</td>
            <td class="rate" :class="changeClass(coin.change)">
              {{ formatRate(coin.change_rate) }}
            </td>
            <td class="volume">{{ formatVolume(coin.acc_trade_price_24h) }}</td>
          </tr>
        </tbody>
      </table>
    </section>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useCryptoStore } from '@/stores/crypto'
import { useAuthStore } from '@/stores/auth'
import ToastNotification from '@/components/crypto/ToastNotification.vue'

const cryptoStore = useCryptoStore()
const authStore = useAuthStore()
const toastRef = ref(null)
const isSyncing = ref(false)

onMounted(async () => {
  // 변동률 알림 콜백 등록
  cryptoStore.setAlertCallback((toast) => {
    toastRef.value?.add(toast)
  })
  await cryptoStore.startPolling()
  if (authStore.isLoggedIn) {
    await cryptoStore.loadWatchlist()
  }
})

onUnmounted(() => {
  cryptoStore.stopPolling()
  cryptoStore.setAlertCallback(null)
})

async function handleSync() {
  isSyncing.value = true
  try {
    await cryptoStore.syncMarkets()
    toastRef.value?.add({
      type: 'up',
      name: '동기화 완료',
      message: `${cryptoStore.coins.length}개 코인 업데이트됨`,
    })
  } finally {
    isSyncing.value = false
  }
}

// ── 포맷 헬퍼 ────────────────────────────────────────────
function formatPrice(price) {
  if (price == null) return '-'
  return price >= 100
    ? price.toLocaleString('ko-KR') + ' 원'
    : price.toFixed(4) + ' 원'
}

function formatRate(rate) {
  if (rate == null) return '-'
  return (rate >= 0 ? '+' : '') + (rate * 100).toFixed(2) + '%'
}

function formatVolume(vol) {
  if (vol == null) return '-'
  if (vol >= 1_000_000_000_000) return (vol / 1_000_000_000_000).toFixed(1) + '조'
  if (vol >= 100_000_000) return (vol / 100_000_000).toFixed(1) + '억'
  return vol.toLocaleString('ko-KR')
}

function changeClass(change) {
  if (change === 'RISE') return 'up'
  if (change === 'FALL') return 'down'
  return 'flat'
}
</script>

<style scoped>
.dashboard { padding: 1.5rem; max-width: 1200px; margin: 0 auto; }
.section-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 0.75rem; }
.divider { border: none; border-top: 1px solid #e5e7eb; margin: 1.5rem 0; }

.fav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
}
.fav-card {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 0.875rem;
  cursor: pointer;
  transition: box-shadow 0.15s;
}
.fav-card:hover { box-shadow: 0 2px 10px rgba(0,0,0,0.08); }
.fav-card-header { display: flex; justify-content: space-between; align-items: center; }
.coin-kor { font-weight: 600; font-size: 0.95rem; }
.fav-card-market { font-size: 0.72rem; color: #9ca3af; margin-top: 0.2rem; }
.fav-card-price { font-size: 1rem; font-weight: 600; margin-top: 0.5rem; }
.fav-card-rate { font-size: 0.85rem; margin-top: 0.15rem; }

/* 툴바 */
.toolbar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}
.search-input {
  flex: 1;
  max-width: 360px;
  padding: 0.5rem 0.875rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.9rem;
  outline: none;
}
.search-input:focus { border-color: #6366f1; box-shadow: 0 0 0 2px #6366f120; }

.sync-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}
.sync-btn:hover:not(:disabled) { background: #f3f4f6; }
.sync-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.coin-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.coin-table th {
  text-align: left;
  padding: 0.5rem 0.75rem;
  border-bottom: 2px solid #e5e7eb;
  color: #6b7280;
  font-weight: 500;
  white-space: nowrap;
}
.coin-row { cursor: pointer; }
.coin-row:hover { background: #f9fafb; }
.coin-row td { padding: 0.5rem 0.75rem; border-bottom: 1px solid #f3f4f6; }

.name-cell { display: flex; flex-direction: column; }
.kor { font-weight: 500; }
.eng { font-size: 0.72rem; color: #9ca3af; }
.market-code { color: #6b7280; font-size: 0.8rem; }
.price { font-weight: 600; text-align: right; }
.rate { text-align: right; font-weight: 500; }
.volume { text-align: right; color: #6b7280; }

.up { color: #ef4444; }
.down { color: #3b82f6; }
.flat { color: #6b7280; }

.star-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
  color: #d1d5db;
  padding: 0;
  line-height: 1;
  transition: color 0.1s;
}
.star-btn.active { color: #f59e0b; }
.star-btn:hover { color: #f59e0b; }

.empty-msg { color: #9ca3af; font-size: 0.9rem; padding: 0.5rem 0; }
.loading { color: #9ca3af; padding: 2rem 0; text-align: center; }
</style>