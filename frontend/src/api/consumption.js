// src/api/consumption.js
import axios from 'axios'

const BASE = '/api/consumption'

const authHeader = () => {
  // 🚨 [수정 완료] auth.js 금고 이름에 맞춰 'token' 대신 'access'를 꺼내옵니다!
  const token = localStorage.getItem('access')
  
  return {
    headers: { 
      Authorization: token ? `Bearer ${token}` : '' 
    }
  }
}

// 아래 getMonthlyCalendar, getInsight, getInsightTrend 등 기존 코드는 그대로 유지!
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

export const toggleSettleTarget = (txId) =>
  axios.patch(`${BASE}/transactions/${txId}/settle-target/`, {}, authHeader())

export const calculateSettle = (txId, peopleCount) =>
  axios.patch(`${BASE}/transactions/${txId}/settle-calculate/`, { people_count: peopleCount }, authHeader())

export const completeSettle = (txId) =>
  axios.patch(`${BASE}/transactions/${txId}/settle-complete/`, {}, authHeader())

export const getSettleDashboard = () =>
  axios.get(`${BASE}/settle/dashboard/`, authHeader())

export const removeSettle = (txId) =>
  axios.delete(`${BASE}/transactions/${txId}/settle-remove/`, authHeader())