// frontend/src/api/crypto.js
import axios from './axios'

export const cryptoAPI = {
  // ── 마켓 목록 + 실시간 시세 ─────────────────────────────
  getCoins() {
    return axios.get('/api/crypto/markets/')
  },

  // ── 코인 상세 (캔들 포함) ────────────────────────────────
  getCoinDetail(market) {
    return axios.get(`/api/crypto/coins/${market}/`)
  },

  // ── 즐겨찾기 목록 ────────────────────────────────────────
  getFavorites() {
    return axios.get('/api/crypto/watchlist/')
  },

  // ── 즐겨찾기 추가  { coin_symbol: "BTC" } ────────────────
  addFavorite(coinSymbol) {
    return axios.post('/api/crypto/watchlist/', { coin_symbol: coinSymbol })
  },

  // ── 즐겨찾기 삭제 ────────────────────────────────────────
  removeFavorite(coinSymbol) {
    return axios.delete(`/api/crypto/watchlist/${coinSymbol}/`)
  },

  // ── 마켓 캐시 동기화 ─────────────────────────────────────
  syncMarkets() {
    return axios.post('/api/crypto/markets/sync/')
  },

  // ── Social Buzz ──────────────────────────────────────────
  getBuzzList() {
    return axios.get('/api/crypto/buzz/')
  },
  getBuzzDetail(coinSymbol) {
    return axios.get(`/api/crypto/buzz/${coinSymbol}/`)
  },
  getBuzzScore() {
    return axios.get('/api/crypto/buzz/score/')
  },

  // ── 감성 분석 ────────────────────────────────────────────
  getSentimentList() {
    return axios.get('/api/crypto/sentiment/')
  },
  getSentimentDetail(coinSymbol) {
    return axios.get(`/api/crypto/sentiment/${coinSymbol}/`)
  },

  // ── 감성 분석 실행 (GPT) ─────────────────────────────────
  analyzeSentiment(coinSymbol, coinName = '') {
    return axios.post('/api/crypto/sentiment/analyze/', {
      coin_symbol: coinSymbol,
      coin_name:   coinName,
    })
  },

  // ── 감성 분석 캐시 조회 ──────────────────────────────────
  getSentimentCached(coinSymbol) {
    return axios.get(`/api/crypto/sentiment/${coinSymbol}/cached/`)
  },
}