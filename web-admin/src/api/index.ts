import axios from 'axios'
import { useRouter } from 'vue-router'

const api = axios.create({ baseURL: '/api/admin' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      const router = useRouter()
      router.push('/login')
    }
    return Promise.reject(err)
  }
)

export default api
