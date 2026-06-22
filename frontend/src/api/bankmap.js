// src/api/bankmap.js
import axios from 'axios'

const BASE = '/api/bankmap'

export const searchBanks = (province, district, brand) =>
  axios.get(`${BASE}/search/`, { params: { province, district, brand } })

export const getDirections = (startX, startY, endX, endY) =>
  axios.get(`${BASE}/directions/`, {
    params: { start_x: startX, start_y: startY, end_x: endX, end_y: endY },
  })