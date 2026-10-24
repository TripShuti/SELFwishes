const bridgeApi = globalThis.browser || globalThis.chrome
const requiredCookies = ['account_id_v2', 'account_mid_v2', 'cookie_token_v2']

async function connectBrowser(message, sender) {
  if (!sender.tab || sender.frameId !== 0) throw new Error('Open SELFwishes in a browser tab.')
  const origin = new URL(sender.url).origin
  const { services = [] } = await bridgeApi.storage.local.get('services')
  if (!services.includes(origin)) throw new Error('Enable this SELFwishes address in the extension first.')
  const tabOrigin = new URL(sender.tab.url).origin
  if (tabOrigin !== origin) throw new Error('The service tab changed. Try again.')
  const uid = message.uid || null
  if (uid !== null && !/^[0-9]{8,12}$/.test(uid)) throw new Error('Invalid character UID.')
  const stores = await bridgeApi.cookies.getAllCookieStores()
  const store = stores.find(item => item.tabIds.includes(sender.tab.id))
  if (!store) throw new Error('Cannot access this browser cookie store.')
  // Keep each domain and cookie store separate: never mix two accounts.
  let cookies
  for (const domain of ['hoyoverse.com', 'hoyolab.com']) {
    const found = await bridgeApi.cookies.getAll({ domain, storeId: store.id })
    const exactDomain = found.filter(cookie => cookie.domain.replace(/^\./, '') === domain &&
      !cookie.partitionKey && (!cookie.expirationDate || cookie.expirationDate > Date.now() / 1000))
    const selected = Object.fromEntries(requiredCookies.map(name => [name,
      exactDomain.find(cookie => cookie.name === name)?.value]))
    if (requiredCookies.every(name => selected[name])) {
      cookies = selected
      break
    }
  }
  if (!cookies) throw new Error('Sign in to your HoYoverse account in this browser, then try again.')
  let response
  try {
    // Send credentials directly from the extension to the approved server.
    // The page/content script receives only public connection metadata.
    response = await fetch(origin + '/api/import/hoyoverse/connect', {
      method: 'POST', redirect: 'error', credentials: 'omit',
      headers: { 'Content-Type': 'application/json', 'X-SELFwishes-Bridge': '1' },
      body: JSON.stringify({ cookies, expected_uid: uid }),
      signal: AbortSignal.timeout(45000),
    })
  } catch {
    throw new Error('Cannot reach SELFwishes. Check the service address and network.')
  }
  let data
  try { data = await response.json() } catch { throw new Error('Invalid SELFwishes response. Update the server.') }
  if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Connection failed.')
  return { roles: data.roles.map(role => ({ uid: role.uid, region: role.region, nickname: role.nickname })) }
}

bridgeApi.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type !== 'SELFWISHES_CONNECT') return false
  connectBrowser(message, sender).then(
    result => sendResponse({ ok: true, ...result }),
    error => sendResponse({ ok: false, error: error.message || 'Connection failed.' }),
  )
  return true
})


// A persistent tab keeps Firefox permission prompts alive and visible.
bridgeApi.action.onClicked.addListener(tab => {
  bridgeApi.tabs.create({ url: bridgeApi.runtime.getURL('popup.html') + '?tab=' + tab.id })
})
