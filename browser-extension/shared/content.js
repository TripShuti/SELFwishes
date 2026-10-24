(() => {
  if (globalThis.selfwishesBridgeLoaded || window.top !== window) return
  if (!document.querySelector('meta[name="selfwishes-app"][content="1"]')) return
  globalThis.selfwishesBridgeLoaded = true
  const api = globalThis.browser || globalThis.chrome
  let pending = false
  const respond = data => window.postMessage({ source: 'SELFwishes-extension', ...data }, location.origin)
  window.addEventListener('message', async event => {
    if (event.source !== window || event.origin !== location.origin || event.data?.source !== 'SELFwishes-app') return
    const { type, requestId, uid } = event.data
    if (type === 'PING') {
      respond({ type: 'READY', version: api.runtime.getManifest().version })
      return
    }
    if (type !== 'CONNECT' || typeof requestId !== 'string' || requestId.length > 80) return
    if (pending) {
      respond({ type: 'RESULT', requestId, ok: false, error: 'A browser connection is already running.' })
      return
    }
    pending = true
    try {
      const result = await api.runtime.sendMessage({ type: 'SELFWISHES_CONNECT', uid })
      respond({ type: 'RESULT', requestId, ...result })
    } catch {
      respond({ type: 'RESULT', requestId, ok: false, error: 'Reload the page and enable the SELFwishes extension.' })
    } finally {
      pending = false
    }
  })
  respond({ type: 'READY', version: api.runtime.getManifest().version })
})()
