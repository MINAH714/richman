// src/api/consumption.js
import axios from 'axios'

const BASE = 'http://localhost:5173/api/consumption'

// ❌ 기존 코드
// const authHeader = () => ({
//   headers: { Authorization: `Bearer ${localStorage.getItem('access')}` }
// })

// 🛠️ 임시 수정 코드: ssafy 계정의 access 토큰을 직접 문자열로 박아버립니다.
const authHeader = () => ({
  headers: { 
    Authorization: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzgxNTEzMzE0LCJpYXQiOjE3ODE0MjY5MTQsImp0aSI6IjRjYzQ5YzFmMjQ0NDQzYTI4ZmJkOGVlOWNjNzI1OWI0IiwidXNlcl9pZCI6IjEifQ.WfEzbO_AxDxX5bD9EZP7MmN5Fy2jNyCDiSGFIKXVKOU' 
  }
})

export const getMonthlyCalendar = (year, month) =>
  axios.get(`${BASE}/calendar/`, { params: { year, month }, ...authHeader() })

export const getDayDetail = (dateStr) =>
  axios.get(`${BASE}/calendar/${dateStr}/`, authHeader())

export const updateCategory = (txId, category) =>
  axios.patch(`${BASE}/transactions/${txId}/category/`, { category }, authHeader())