// ----  Settings basic HTTP client (axios)
import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    // to send images and TXT files
    'Content-Type': 'multipart/form-data',
  },
})

export default apiClient
