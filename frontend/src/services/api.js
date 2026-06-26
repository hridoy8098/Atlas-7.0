// src/services/api.js — Atlas 7.0 API Service
import axios from 'axios'

const api = axios.create({ baseURL: '/api', timeout: 15000 })

// ===== AUTH =====
export const verifyPin = (pin) => api.post('/auth/pin', { pin }).then(r => r.data)
export const lockSystem = () => api.post('/auth/logout').then(r => r.data)

// ===== COMMAND =====
export const sendCommand = (command) => api.post('/command', { command }).then(r => r.data)

// ===== SYSTEM =====
export const getMetrics = () => api.get('/system/metrics').then(r => r.data)
export const getWeather = () => api.get('/system/weather').then(r => r.data)
export const getPrayerTimes = () => api.get('/system/prayer-times').then(r => r.data)
export const getGroqStatus = () => api.get('/system/groq-status').then(r => r.data)

// ===== CONFIG =====
export const getUserConfig = () => api.get('/config').then(r => r.data)

// ===== AGENTS =====
export const optimizePC = () => api.post('/agent/optimize-pc').then(r => r.data)
export const cleanTemp = () => api.post('/agent/clean-temp').then(r => r.data)
export const listFiles = (path = '') => api.get('/agent/list-files?path=' + encodeURIComponent(path)).then(r => r.data)
export const searchFiles = (q) => api.get('/agent/search-files?query=' + encodeURIComponent(q)).then(r => r.data)
export const organizeDownloads = () => api.post('/agent/organize-downloads').then(r => r.data)
export const executeCommand = (cmd) => api.post('/agent/execute', { cmd }).then(r => r.data)

// ===== ML AGENT =====
export const uploadMLFile = (file, fileType = 'auto') => {
  const form = new FormData()
  form.append('file', file)
  form.append('file_type', fileType)
  return api.post('/ml/upload', form).then(r => r.data)
}
export const analyzeMLData = (data) => api.post('/ml/analyze', { data }).then(r => r.data)
export const trainMLModel = (params) => api.post('/ml/train', params).then(r => r.data)
export const predictML = (modelId, input) => api.post('/ml/predict', { model_id: modelId, input }).then(r => r.data)
export const listMLModels = () => api.get('/ml/models').then(r => r.data)
export const deleteMLModel = (id) => api.delete(`/ml/models/${encodeURIComponent(id)}`).then(r => r.data)
export const generateMLPlot = (params) => api.post('/ml/plot', params).then(r => r.data)
export const getMLChartData = (params) => api.post('/ml/plot', params).then(r => r.data)
export const getMLJobStatus = (jobId) => api.get(`/ml/jobs/${encodeURIComponent(jobId)}`).then(r => r.data)
export const getMLModelInfo = (modelId) => api.get(`/ml/models/${encodeURIComponent(modelId)}`).then(r => r.data)
export const clusterMLData = (params) => api.post('/ml/cluster', params).then(r => r.data)
export const dimReduceML = (params) => api.post('/ml/dimreduce', params).then(r => r.data)
export const trainMLNeural = (params) => api.post('/ml/neural', params).then(r => r.data)
export const tuneMLHyperparams = (params) => api.post('/ml/tune', params).then(r => r.data)
export const kfoldML = (params) => api.post('/ml/kfold', params).then(r => r.data)
export const featureEngineerML = (params) => api.post('/ml/feature_engineer', params).then(r => r.data)
export const evaluateML = (params) => api.post('/ml/evaluate', params).then(r => r.data)

// ===== WEBSOCKET =====
export const createWebSocket = (onMessage) => {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const ws = new WebSocket(`${protocol}//${window.location.host}/ws`)
  ws.onopen = () => {
    console.log('🔌 Atlas WS connected')
    setInterval(() => { if (ws.readyState === WebSocket.OPEN) ws.send('ping') }, 30000)
  }
  ws.onmessage = (e) => {
    try { onMessage(JSON.parse(e.data)) } catch {}
  }
  ws.onerror = (e) => console.error('WS error:', e)
  return ws
}

export default api