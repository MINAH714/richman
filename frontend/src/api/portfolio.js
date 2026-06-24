// frontend/src/api/portfolio.js
import axios from './axios'


export const deletePortfolioItem = (id) =>
  axios.delete(`/api/portfolio/${id}/delete/`)

export const updateStockQuantity = (id, quantity) =>
  axios.put(`/api/portfolio/${id}/update-quantity/`, { quantity })

// ⭐ [신규 추가] 현금 자산 추가
export const addCashHolding = (payload) =>
  axios.post('/api/portfolio/cash/add/', payload)

export const addCryptoHolding = (payload) =>
  axios.post('/api/portfolio/crypto/add/', payload)