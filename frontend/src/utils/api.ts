// API client — thin wrapper around axios for all backend calls
// TODO: add interceptors for auth token and error handling

import axios from 'axios'

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1',
})

// TODO: export typed functions — fetchThreats(), fetchVulns(), fetchRBACEvents(), getRiskScore()
