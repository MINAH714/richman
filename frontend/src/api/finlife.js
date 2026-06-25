// frontend/src/api/finlife.js
import axios from '@/api/axios'

export const finlifeAPI = {
  getProducts(bank = '') {
    const params = bank && bank !== '전체' ? { bank } : {}
    // /finlife/ -> /api/finlife/ 로 변경
    return axios.get('/api/finlife/', { params })
  },

  getProductDetail(finPrdtCd) {
    // /finlife/ -> /api/finlife/ 로 변경
    return axios.get(`/api/finlife/${finPrdtCd}/`)
  },

  joinProduct(finPrdtCd) {
    // /finlife/ -> /api/finlife/ 로 변경
    return axios.post(`/api/finlife/${finPrdtCd}/join/`)
  },
  saveProducts() {
    return axios.get('/api/finlife/save/') 
  }
}