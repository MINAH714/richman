// src/api/consumption.js
import axios from 'axios'

// 🚨 도메인 없이 '/api/consumption'만 적혀 있어야 vite.config.js의 프록시가 작동합니다!
const BASE = '/api/consumption'

const authHeader = () => ({
  headers: { 
    // ⚠️ 'Bearer ' 뒤에 방금 터미널에서 얻은 아주 긴 토큰을 정확히 붙여넣으세요.
    // (끝에 따옴표 탈출 기호가 없는지, 싱글 쿼테이션 ' ' 사이에 잘 들어갔는지 확인!)
    Authorization: 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzgxNTk1MTYxLCJpYXQiOjE3ODE1MDg3NjEsImp0aSI6IjdjMDZhYWJjNzYyZTQ1NjNhZjU1NmM1MzZlZTI4ODEyIiwidXNlcl9pZCI6IjEifQ.toPBzy9mdYNUjQrdDbb-kIrcVZRlOCMiycyDb7r8KAI' 
  }
})

export const getMonthlyCalendar = (year, month) =>
  axios.get(`${BASE}/calendar/`, { params: { year, month }, ...authHeader() })

export const getDayDetail = (dateStr) =>
  axios.get(`${BASE}/calendar/${dateStr}/`, authHeader())

export const updateCategory = (txId, category) =>
  axios.patch(`${BASE}/transactions/${txId}/category/`, { category }, authHeader())

export const getInsight = (year, month) =>
  axios.get(`${BASE}/insight/`, { params: { year, month }, ...authHeader() })

export const getInsightTrend = (year, month) =>
  axios.get(`${BASE}/insight/trend/`, { params: { year, month }, ...authHeader() })