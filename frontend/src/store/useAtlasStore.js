// store/useAtlasStore.js — Zustand global state
import { create } from 'zustand'

const useAtlasStore = create((set, get) => ({
  // Auth
  isAuthenticated: false,
  sessionToken: null,
  userName: 'Boss',

  // UI
  activePanel: 'chat',

  // Chat
  messages: [],
  isProcessing: false,

  // System metrics
  metrics: { cpu: 0, mem_used: 0, mem_percent: 0, disk_percent: 0, bat_percent: -1, bat_charging: false },

  // ML
  mlDataset: null,
  mlAnalysis: null,
  mlModels: [],
  mlTrainingStatus: null,
  mlTrainingResult: null,
  mlPredictionResult: null,
  mlPlotImage: null,
  mlPlotData: null,
  mlClusterResult: null,
  mlDimRedResult: null,
  mlNeuralResult: null,
  mlTuneResult: null,
  mlKfoldResult: null,
  mlFeatEngResult: null,
  mlEvaluationData: null,

  // Weather
  weather: { temp: 30, desc: 'Partly Cloudy', humidity: 65, wind: 12, city: 'Dhaka' },

  // Prayer times
  prayerTimes: { fajr: '--:--', dhuhr: '--:--', asr: '--:--', maghrib: '--:--', isha: '--:--' },

  // WebSocket
  ws: null,

  // ===== ACTIONS =====
  setAuthenticated: (token) => set({ isAuthenticated: true, sessionToken: token }),
  logout: () => set({ isAuthenticated: false, sessionToken: null, messages: [] }),
  setUserName: (name) => set({ userName: name }),
  setActivePanel: (panel) => set({ activePanel: panel }),
  setMetrics: (metrics) => set({ metrics }),
  setWeather: (weather) => set({ weather }),
  setMLDataset: (d) => set({ mlDataset: d, mlAnalysis: null }),
  setMLAnalysis: (a) => set({ mlAnalysis: a }),
  setMLModels: (m) => set({ mlModels: m }),
  setMLTrainingStatus: (s) => set({ mlTrainingStatus: s }),
  setMLTrainingResult: (r) => set({ mlTrainingResult: r, mlTrainingStatus: r ? 'done' : null }),
  setMLPredictionResult: (r) => set({ mlPredictionResult: r }),
  setMLPlotImage: (i) => set({ mlPlotImage: i }),
  setMLPlotData: (d) => set({ mlPlotData: d }),
  setMLClusterResult: (r) => set({ mlClusterResult: r }),
  setMLDimRedResult: (r) => set({ mlDimRedResult: r }),
  setMLNeuralResult: (r) => set({ mlNeuralResult: r, mlTrainingStatus: r ? 'done' : null }),
  setMLTuneResult: (r) => set({ mlTuneResult: r }),
  setMLKfoldResult: (r) => set({ mlKfoldResult: r }),
  setMLFeatEngResult: (r) => set({ mlFeatEngResult: r }),
  setMLEvaluationData: (d) => set({ mlEvaluationData: d }),
  setPrayerTimes: (prayerTimes) => set({ prayerTimes }),
  setWs: (ws) => set({ ws }),
  setProcessing: (v) => set({ isProcessing: v }),

  addMessage: (role, text) => set(state => ({
    messages: [...state.messages, {
      id: Date.now() + Math.random(),
      role,
      text,
      time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    }]
  })),

  clearMessages: () => set({ messages: [] }),
}))

export default useAtlasStore
