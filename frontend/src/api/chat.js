// frontend/src/api/chat.js
import axios from './axios'

export const chatAPI = {
  // 세션 생성
  createSession() {
    return axios.post('/api/chat/sessions/')
  },

  // 세션 목록
  getSessions() {
    return axios.get('/api/chat/sessions/')
  },

  // 메시지 전송
  sendMessage(sessionId, content) {
    return axios.post(`/api/chat/sessions/${sessionId}/messages/`, { content })
  },

  // 메시지 목록
  getMessages(sessionId) {
    return axios.get(`/api/chat/sessions/${sessionId}/messages/`)
  },
}