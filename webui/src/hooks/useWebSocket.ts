import { useEffect, useRef } from 'react'
import { useCrawlerStore } from '@/store/crawlerStore'
import type { LogEntry } from '@/types/crawler'

// Module-level singleton to ensure only one global WebSocket connection
let globalWs: WebSocket | null = null
let globalReconnectTimer: ReturnType<typeof setTimeout> | null = null
let connectionCount = 0 // Track number of active consumers

export function useLogWebSocket() {
  const addLog = useCrawlerStore((state) => state.addLog)
  const addLogRef = useRef(addLog)

  // Keep addLog reference updated
  useEffect(() => {
    addLogRef.current = addLog
  }, [addLog])

  useEffect(() => {
    connectionCount++

    const connect = () => {
      if (globalReconnectTimer) {
        clearTimeout(globalReconnectTimer)
        globalReconnectTimer = null
      }

      // If already connected or connecting, do not re-create
      if (globalWs && (globalWs.readyState === WebSocket.OPEN || globalWs.readyState === WebSocket.CONNECTING)) {
        return
      }

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const host = window.location.host
      const wsUrl = `${protocol}//${host}/api/ws/logs`

      const ws = new WebSocket(wsUrl)
      globalWs = ws

      ws.onopen = () => {
        if (globalWs !== ws) return
        console.log('WebSocket connected')
      }

      ws.onmessage = (event) => {
        if (globalWs !== ws) return
        if (event.data === 'ping') {
          ws.send('pong')
          return
        }
        if (event.data === 'pong') {
          return
        }

        try {
          const log: LogEntry = JSON.parse(event.data)
          if (log.id && log.message) {
            addLogRef.current(log)
          }
        } catch (e) {
          console.warn('Failed to parse WebSocket message:', event.data)
        }
      }

      ws.onclose = () => {
        if (globalWs !== ws) return
        console.log('WebSocket disconnected')
        globalWs = null
        // Reconnect only if there are still consumers
        if (connectionCount > 0) {
          globalReconnectTimer = setTimeout(connect, 2000)
        }
      }

      ws.onerror = (error) => {
        if (globalWs !== ws) return
        console.error('WebSocket error:', error)
      }
    }

    // Initial connect
    connect()

    // Heartbeat
    const heartbeat = setInterval(() => {
      if (globalWs && globalWs.readyState === WebSocket.OPEN) {
        globalWs.send('ping')
      }
    }, 30000)

    return () => {
      connectionCount--
      clearInterval(heartbeat)

      // Disconnect only when no active consumers remain
      if (connectionCount === 0) {
        if (globalReconnectTimer) {
          clearTimeout(globalReconnectTimer)
          globalReconnectTimer = null
        }
        if (globalWs) {
          const ws = globalWs
          globalWs = null
          ws.close()
        }
      }
    }
  }, []) // Empty dependency array

  return { ws: globalWs }
}
