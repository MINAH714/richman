import api from '@/api/axios'

// 회원가입 API 호출 함수
export const signup = (userData) => {
  return api.post('/api/accounts/signup/', userData)
}