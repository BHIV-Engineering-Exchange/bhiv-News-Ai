import { useState, useEffect, useCallback, useRef } from 'react'

interface WebSocketMessage {
    type: string
    data: any
    timestamp: string
}

export function useWebSocket(url: string) {
    const [status, setStatus] = useState<'connecting' | 'open' | 'closed' | 'error'>('connecting')
    const [messages, setMessages] = useState<WebSocketMessage[]>([])
    const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
    const socketRef = useRef<WebSocket | null>(null)

    const connect = useCallback(() => {
        try {
            console.log(`🔌 Connecting to WebSocket: ${url}`)
            const socket = new WebSocket(url)
            socketRef.current = socket

            socket.onopen = () => {
                console.log(`✅ WebSocket Open: ${url}`)
                setStatus('open')
            }

            socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data)
                    const message = {
                        type: data.type || 'unknown',
                        data: data.data || data,
                        timestamp: data.timestamp || new Date().toISOString()
                    }
                    setMessages((prev) => [...prev.slice(-19), message])
                    setLastMessage(message)
                } catch (err) {
                    console.error('Failed to parse WS message:', err)
                }
            }

            socket.onclose = () => {
                console.log(`❌ WebSocket Closed: ${url}`)
                setStatus('closed')
            }

            socket.onerror = (err) => {
                console.error('WebSocket Error:', err)
                setStatus('error')
            }
        } catch (err) {
            console.error('WebSocket Connection Failed:', err)
            setStatus('error')
        }
    }, [url])

    useEffect(() => {
        connect()
        return () => {
            if (socketRef.current) {
                socketRef.current.close()
            }
        }
    }, [connect])

    const sendMessage = useCallback((type: string, data: any) => {
        if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
            socketRef.current.send(JSON.stringify({ type, ...data }))
        } else {
            console.warn('WebSocket not open. Cannot send message.')
        }
    }, [])

    return { status, messages, lastMessage, sendMessage, reconnect: connect }
}
