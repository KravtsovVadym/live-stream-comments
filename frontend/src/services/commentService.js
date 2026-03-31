// ---- (commentService) — API service for comments <

import apiClient from './axios'

export const commentService = {
  // ---- Getting a list of comments (pagination of 25)
  getComments(page = 1, ordering = '-created_at') {
    return apiClient.get(`comments/?page=${page}&ordering=${ordering}`)
  },
  // ---- Getting a CAPTCHA
  getCaptcha() {
    return apiClient.get('captcha/')
  },
  // ---- Creation and submitting a comment
  createComment(formData) {
    return apiClient.post('comints/', formData)
  },
}
