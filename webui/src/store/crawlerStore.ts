import { create } from 'zustand'
import type { LogEntry, CrawlerConfig } from '@/types/crawler'

interface CrawlerState {
  // Status
  status: 'idle' | 'running' | 'stopping' | 'error'
  platform: string | null
  crawlerType: string | null
  startedAt: string | null

  // Logs
  logs: LogEntry[]
  clearedAfterLogId: number | null // After clearing logs, only show logs with id > this value

  // Config
  config: CrawlerConfig

  // Actions
  setStatus: (status: CrawlerState['status']) => void
  setRunningInfo: (platform: string | null, crawlerType: string | null, startedAt: string | null) => void
  addLog: (log: LogEntry) => void
  setLogs: (logs: LogEntry[]) => void
  clearLogs: () => void
  restoreLogs: () => void
  updateConfig: (config: Partial<CrawlerConfig>) => void
  reset: () => void
}

// Key for persistent localStorage
const CLEARED_LOG_ID_KEY = 'mediacrawler_cleared_log_id'

// Read cleared marker from localStorage
function getClearedLogIdFromStorage(): number | null {
  const stored = localStorage.getItem(CLEARED_LOG_ID_KEY)
  if (stored === null) return null
  const value = parseInt(stored, 10)
  return isNaN(value) ? null : value
}

// Save cleared marker to localStorage
function saveClearedLogIdToStorage(id: number | null): void {
  if (id === null) {
    localStorage.removeItem(CLEARED_LOG_ID_KEY)
  } else {
    localStorage.setItem(CLEARED_LOG_ID_KEY, id.toString())
  }
}

const defaultConfig: CrawlerConfig = {
  platform: 'bili',
  login_type: 'qrcode',
  crawler_type: 'search',
  keywords: '',
  specified_ids: '',
  creator_ids: '',
  start_page: 1,
  enable_comments: true,
  enable_sub_comments: false,
  save_option: 'json',
  cookies: '',
  headless: false,
}

export const useCrawlerStore = create<CrawlerState>((set, get) => ({
  status: 'idle',
  platform: null,
  crawlerType: null,
  startedAt: null,
  logs: [],
  clearedAfterLogId: getClearedLogIdFromStorage(), // Initialize from localStorage
  config: defaultConfig,

  setStatus: (status) => {
    set({ status })
    // When a new crawl task starts, clear previous clear-marker
    if (status === 'running') {
      const currentClearedId = get().clearedAfterLogId
      if (currentClearedId !== null) {
        set({ clearedAfterLogId: null })
        saveClearedLogIdToStorage(null)
      }
    }
  },

  setRunningInfo: (platform, crawlerType, startedAt) => {
    set({ platform, crawlerType, startedAt })
    // When setting new run info, also clear previous clear-marker
    if (startedAt !== null) {
      const currentClearedId = get().clearedAfterLogId
      if (currentClearedId !== null) {
        set({ clearedAfterLogId: null })
        saveClearedLogIdToStorage(null)
      }
    }
  },

  addLog: (log) => {
    const { clearedAfterLogId, logs } = get()
    // If there is a cleared marker, filter out logs with id <= marker
    if (clearedAfterLogId !== null && log.id <= clearedAfterLogId) {
      return
    }
    // Prevent duplicate logs from WebSocket reconnects
    if (logs.length > 0 && logs[logs.length - 1].id === log.id) {
      return
    }
    if (logs.some((existing) => existing.id === log.id)) {
      return
    }
    set((state) => ({
      logs: [...state.logs.slice(-499), log], // Keep last 500 logs
    }))
  },

  setLogs: (logs) => {
    const { clearedAfterLogId } = get()
    // If there is a cleared marker, filter out logs with id <= marker
    const filteredLogs = clearedAfterLogId !== null
      ? logs.filter((log) => log.id > clearedAfterLogId)
      : logs
    set({ logs: filteredLogs })
  },

  clearLogs: () => {
    const { logs } = get()
    // Record current max log id; only show logs with larger id afterwards
    const maxLogId = logs.length > 0 ? Math.max(...logs.map((l) => l.id)) : 0
    set({ logs: [], clearedAfterLogId: maxLogId })
    // Persist to localStorage
    saveClearedLogIdToStorage(maxLogId)
  },

  restoreLogs: () => {
    // Clear the clear-marker so all logs show on next reload
    set({ clearedAfterLogId: null })
    saveClearedLogIdToStorage(null)
    // Trigger log reload (via refreshing page or reconnecting WebSocket)
    window.location.reload()
  },

  updateConfig: (config) =>
    set((state) => ({
      config: { ...state.config, ...config },
    })),

  reset: () =>
    set({
      status: 'idle',
      platform: null,
      crawlerType: null,
      startedAt: null,
    }),
}))
