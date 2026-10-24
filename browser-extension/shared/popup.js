const popupApi = globalThis.browser || globalThis.chrome
const enableButton = document.getElementById('enable')
const statusText = document.getElementById('status')
let currentTab
let serviceOrigin
let hostPattern

async function initialize() {
  try {
    const tabId = Number(new URLSearchParams(location.search).get('tab'))
    if (!Number.isInteger(tabId) || tabId <= 0) throw new Error()
    const tab = await popupApi.tabs.get(tabId)
    const url = new URL(tab.url)
    if (!['http:', 'https:'].includes(url.protocol)) throw new Error()
    const [result] = await popupApi.scripting.executeScript({ target: { tabId: tab.id },
      func: () => !!document.querySelector('meta[name="selfwishes-app"][content="1"]'),
    })
    if (!result.result) throw new Error()
    currentTab = tab
    serviceOrigin = url.origin
    hostPattern = `${url.protocol}//${url.hostname}/*`
    document.getElementById('address').textContent = serviceOrigin
    enableButton.disabled = false
  } catch {
    statusText.textContent = 'Open the SELFwishes service tab first, then reopen this popup.'
  }
}

enableButton.addEventListener('click', async () => {
  if (!currentTab) return
  try {
    // Permission requests must start directly from the user's click.
    const allowed = await popupApi.permissions.request({ origins: [hostPattern] })
    if (!allowed) { statusText.textContent = 'Permission was not granted.'; return }
    enableButton.disabled = true
    const { services = [] } = await popupApi.storage.local.get('services')
    await popupApi.storage.local.set({ services: [...new Set([...services, serviceOrigin])] })
    const id = 'selfwishes-' + Array.from(serviceOrigin).reduce((n, c) => ((n * 31) + c.charCodeAt(0)) >>> 0, 0)
    const scripts = await popupApi.scripting.getRegisteredContentScripts({ ids: [id] })
    if (!scripts.length) await popupApi.scripting.registerContentScripts([{
      id, matches: [hostPattern], js: ['content.js'], runAt: 'document_idle', persistAcrossSessions: true,
    }])
    await popupApi.scripting.executeScript({ target: { tabId: currentTab.id }, files: ['content.js'] })
    statusText.textContent = 'Ready. Return to SELFwishes and click Update from browser.'
    document.getElementById('return').hidden = false
  } catch {
    enableButton.disabled = false
    statusText.textContent = 'Could not enable the extension. Reload SELFwishes and try again.'
  }
})
document.getElementById('return').addEventListener('click', async () => {
  if (currentTab) await popupApi.tabs.update(currentTab.id, { active: true })
})
initialize()
