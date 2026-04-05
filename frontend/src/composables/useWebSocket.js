import { ref, onMounted, onUnmounted } from 'vue'

// ---- WebSocket
export function useWebSocket(url, onMessage) {
  const socket = ref(null)

  // ---- WebSocket connection
  const connectWebSocket = () => {
    socket.value = new WebSocket(url)

    // ---- Parse incoming messages and trigger callback
    socket.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      onMessage(data)
    }

    socket.value.onclose = () => {
      console.log('WebSocket closed. Reconnecting in 5 sec...')
      setTimeout(connectWebSocket, 5000)
    }

    // ---- Log connect errors
    socket.value.onerror = (err) => {
      console.error('WebSocket error:', err)
    }
  }

  onMounted(() => {
    connectWebSocket()
  })

  onUnmounted(() => {
    if (socket.value) socket.value.close()
  })

  return { socket }
}
