// API client — thin wrapper around axios for all backend calls
import axios from 'axios'

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1',
  timeout: 15000,
})

// Convenience typed wrappers (used by some components / future)
export const api = {
  getThreats: (params?: Record<string, any>) => apiClient.get('/threats', { params }).then(r => r.data),
  getVulns: (params?: Record<string, any>) => apiClient.get('/vulns', { params }).then(r => r.data),
  getRBAC: (params?: Record<string, any>) => apiClient.get('/rbac', { params }).then(r => r.data),
  getRiskScore: () => apiClient.get('/risk-score').then(r => r.data),
  seed: () => apiClient.post('/seed').then(r => r.data),
}
