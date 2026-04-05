// ---- (commentService) — API service for comments

import apiClient from './axios'

export const commentService = {
  // ---- List of comments
  getComments(page = 1, ordering = '-created_at') {
    return apiClient.get(`comments/?page=${page}&ordering=${ordering}`)
  },
  // ---- CAPTCHA
  getCaptcha() {
    return apiClient.get('captcha/')
  },
  // ---- Creation and submitting a comment
  createComment(formData) {
    return apiClient.post('comments/', formData, {
      headers: {
        'content-type': 'multipart/form-data',
      },
    })
  },
}
