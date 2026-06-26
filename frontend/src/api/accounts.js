// src/api/accounts.js (없으면 새로 생성, 있으면 추가)
import axios from '@/api/axios'

export const getMyInfo = () => axios.get('/api/accounts/me/')
export const getOnboardingInfo = () => axios.get('/api/accounts/onboarding/')