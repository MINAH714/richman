import axios from './axios'

export const cryptoAPI = {
  // 코인 목록 + 실시간 시세
  getCoins() {
    return axios.get('/api/crypto/coins/')
  },

  // 코인 상세 (캔들 포함)
  getCoinDetail(market) {
    return axios.get(`/api/crypto/coins/${market}/`)
  },

  // 즐겨찾기 목록
  getFavorites() {
    return axios.get('/api/crypto/favorites/')
  },

  // 즐겨찾기 추가
  addFavorite(coinId) {
    return axios.post('/api/crypto/favorites/', { coin_id: coinId })
  },

  // 즐겨찾기 삭제
  removeFavorite(coinId) {
    return axios.delete(`/api/crypto/favorites/${coinId}/`)
  },

  // 마켓 DB 동기화 (최초 1회 또는 관리자)
  syncMarkets() {
    return axios.post('/api/crypto/sync/')
  },
}