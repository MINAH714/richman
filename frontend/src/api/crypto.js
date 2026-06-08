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

  // ── Social Buzz (Day 2) ──────────────────────────────────
  getBuzzList() {
    return axios.get('/api/crypto/buzz/')
  },
  getBuzzDetail(coinSymbol) {
    return axios.get(`/api/crypto/buzz/${coinSymbol}/`)
  },

  // ── 감성 분석 (Day 3) ────────────────────────────────────
  getSentimentList() {
    return axios.get('/api/crypto/sentiment/')
  },
  getSentimentDetail(coinSymbol) {
    return axios.get(`/api/crypto/sentiment/${coinSymbol}/`)
  },
}