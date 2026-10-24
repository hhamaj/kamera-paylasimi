import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'

// Server'daki /ws/view'a baglanir; kamera listesini ve her kameranin son karesini tutar.
export function useCameraFeed() {
  const cameras = ref([])
  const frames = reactive({}) // kamera id -> blob URL
  const connected = ref(false)

  let ws = null
  let reconnectTimer = null
  let stopped = false

  function setFrame(id, url) {
    if (frames[id]) URL.revokeObjectURL(frames[id])
    frames[id] = url
  }

  function clearFrame(id) {
    if (frames[id]) URL.revokeObjectURL(frames[id])
    delete frames[id]
  }

  function onMessage(event) {
    if (typeof event.data === 'string') {
      const msg = JSON.parse(event.data)
      if (msg.type === 'cameras') {
        cameras.value = msg.cameras
        const live = new Set(msg.cameras.map((c) => String(c.id)))
        for (const id of Object.keys(frames)) {
          if (!live.has(id)) clearFrame(id)
        }
      }
      return
    }
    const id = new DataView(event.data).getUint32(0)
    const blob = new Blob([event.data.slice(4)], { type: 'image/jpeg' })
    setFrame(id, URL.createObjectURL(blob))
  }

  function connect() {
    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:'
    ws = new WebSocket(`${proto}//${location.host}/ws/view`)
    ws.binaryType = 'arraybuffer'
    ws.onopen = () => (connected.value = true)
    ws.onmessage = onMessage
    ws.onclose = () => {
      connected.value = false
      cameras.value = []
      for (const id of Object.keys(frames)) clearFrame(id)
      if (!stopped) reconnectTimer = setTimeout(connect, 2000)
    }
  }

  onMounted(connect)
  onBeforeUnmount(() => {
    stopped = true
    clearTimeout(reconnectTimer)
    ws?.close()
  })

  return { cameras, frames, connected }
}
