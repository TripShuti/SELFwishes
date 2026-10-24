import { ref } from 'vue'

export const browserBridgeReady = ref(false)
const pending = new Map()

window.addEventListener('message', event => {
  if (event.source !== window || event.origin !== location.origin ||
      event.data?.source !== 'SELFwishes-extension') return
  if (event.data.type === 'READY') browserBridgeReady.value = true
  if (event.data.type !== 'RESULT') return
  const request = pending.get(event.data.requestId)
  if (!request) return
  pending.delete(event.data.requestId)
  clearTimeout(request.timer)
  if (event.data.ok) request.resolve(event.data.roles)
  else request.reject(new Error(event.data.error || 'Browser connection failed.'))
})

export function checkBrowserBridge() {
  window.postMessage({ source: 'SELFwishes-app', type: 'PING' }, location.origin)
}

export function connectBrowser(uid) {
  const requestId = `${Date.now()}-${Math.random().toString(36).slice(2)}`
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      pending.delete(requestId)
      reject(new Error('The browser extension did not respond. Reload the page and try again.'))
    }, 60000)
    pending.set(requestId, { resolve, reject, timer })
    window.postMessage({ source: 'SELFwishes-app', type: 'CONNECT', requestId, uid }, location.origin)
  })
}
