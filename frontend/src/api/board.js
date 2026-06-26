// src/api/board.js
import axios from 'axios'

const BASE = '/api/board'

const authHeader = () => {
  const token = localStorage.getItem('access')
  return { headers: { Authorization: token ? `Bearer ${token}` : '' } }
}

// 게시글
export const getPosts = (category = '') =>
  axios.get(`${BASE}/posts/`, { params: category ? { category } : {} })

export const getPostDetail = (postId) =>
  axios.get(`${BASE}/posts/${postId}/`, authHeader())

export const createPost = (payload) =>
  axios.post(`${BASE}/posts/`, payload, authHeader())

export const updatePost = (postId, payload) =>
  axios.patch(`${BASE}/posts/${postId}/`, payload, authHeader())

export const deletePost = (postId) =>
  axios.delete(`${BASE}/posts/${postId}/`, authHeader())

// 댓글
export const createComment = (postId, content) =>
  axios.post(`${BASE}/posts/${postId}/comments/`, { content }, authHeader())

export const updateComment = (commentId, content) =>
  axios.patch(`${BASE}/comments/${commentId}/`, { content }, authHeader())

export const deleteComment = (commentId) =>
  axios.delete(`${BASE}/comments/${commentId}/`, authHeader())