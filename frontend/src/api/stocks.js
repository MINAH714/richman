import axios from './axios'   // 기존에 있던 axios 인스턴스 (baseURL, JWT 헤더 등 설정됨)

// ── 관심 종목 (Watchlist) ─────────────────────────────

// 내 관심 종목 전체 조회
export const getWatchlist = () =>
  axios.get('/api/stocks/watchlist/')

// 관심 종목 추가
// payload 예시: { symbol: 'AAPL', name: 'Apple Inc.', market: 'NASDAQ' }
export const addWatchlist = (payload) =>
  axios.post('/api/stocks/watchlist/', payload)

// 관심 종목 삭제
// id: Watchlist 항목의 pk
export const removeWatchlist = (id) =>
  axios.delete(`/api/stocks/watchlist/${id}/`)

// ── 포트폴리오 ────────────────────────────────────────

// 포트폴리오 등록 or 수정 (있으면 수정, 없으면 생성)
// watchlistId: 어떤 관심 종목에 대한 포트폴리오인지
// payload 예시: { quantity: 10, average_price: 150.00 }
export const upsertPortfolio = (watchlistId, payload) =>
  axios.post(`/api/stocks/watchlist/${watchlistId}/portfolio/`, payload)

// ── 현재가 조회 ──────────────────────────────────────

// symbol 예시: 'AAPL', '005930.KS'
export const getStockPrice = (symbol) =>
  axios.get(`/api/stocks/price/${symbol}/`)


// 차트 데이터 조회 (캔들 + 이동평균선 + 볼린저 밴드)
// period 예시: '1mo', '3mo', '6mo', '1y'
export const getStockChart = (symbol, period = '3mo') =>
  axios.get(`/api/stocks/chart/${symbol}/`, { params: { period } })