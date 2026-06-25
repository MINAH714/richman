// src/api/recommend.js
import axios from '@/api/axios'

export const getRecommendations = () =>
  axios.get('/api/recommend/')