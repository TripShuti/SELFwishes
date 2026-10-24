const { test } = require('node:test')
const assert = require('node:assert/strict')
const vm = require('node:vm')
const fs = require('node:fs')
const path = require('node:path')
const source = fs.readFileSync(path.join(__dirname, '../shared/background.js'), 'utf8')

function harness({ approved = true, cookies = [], response } = {}) {
  let listener
  const calls = { cookies: [], requests: [] }
  const api = {
    action: { onClicked: { addListener() {} } },
    runtime: { onMessage: { addListener(fn) { listener = fn } } },
    storage: { local: { async get() { return { services: approved ? ['http://localhost:6767'] : [] } } } },
    cookies: {
      async getAllCookieStores() { return [{ id: 'firefox-container-1', tabIds: [7] }] },
      async getAll(args) { calls.cookies.push(args); return cookies.filter(c => c.domain.replace(/^\./, '') === args.domain) },
    },
  }
  vm.runInNewContext(source, { chrome: api, URL, Date, AbortSignal,
    fetch: async (url, options) => {
      calls.requests.push({ url, options })
      return response || { ok: true, async json() { return { roles: [{ uid: '716004704', region: 'os_euro', nickname: 'Trip' }] } } }
    },
  })
  const send = (message = { type: 'SELFWISHES_CONNECT', uid: '716004704' }, overrides = {}) => new Promise(resolve => {
    const sender = { url: 'http://localhost:6767/dashboard', tab: { id: 7, url: 'http://localhost:6767/dashboard' }, frameId: 0, ...overrides }
    const handled = listener(message, sender, resolve)
    if (!handled) resolve(null)
  })
  return { calls, send }
}
const fullCookies = ['account_id_v2', 'account_mid_v2', 'cookie_token_v2'].map(name => ({ name, value: 'test-secret', domain: '.hoyoverse.com', httpOnly: true }))

test('never reads cookies until a connection request', () => {
  const { calls } = harness({ cookies: fullCookies })
  assert.equal(calls.cookies.length, 0)
  assert.equal(calls.requests.length, 0)
})
test('unapproved service is denied before cookie access', async () => {
  const { send, calls } = harness({ approved: false, cookies: fullCookies })
  assert.equal((await send()).ok, false)
  assert.equal(calls.cookies.length, 0)
})
test('different port and embedded frames are denied', async () => {
  const { send, calls } = harness({ cookies: fullCookies })
  assert.equal((await send(undefined, { url: 'http://localhost:8000/' })).ok, false)
  assert.equal((await send(undefined, { frameId: 1 })).ok, false)
  assert.equal(calls.cookies.length, 0)
})
test('only required cookies go directly to the approved origin', async () => {
  const { send, calls } = harness({ cookies: [...fullCookies, { name: 'unrelated', value: 'do-not-send', domain: '.hoyoverse.com' }] })
  const result = await send()
  assert.equal(result.ok, true)
  assert.equal(JSON.stringify(result).includes('test-secret'), false)
  assert.equal(calls.requests.length, 1)
  const { url, options } = calls.requests[0]
  assert.equal(url, 'http://localhost:6767/api/import/hoyoverse/connect')
  assert.equal(options.redirect, 'error')
  assert.equal(options.credentials, 'omit')
  const body = JSON.parse(options.body)
  assert.deepEqual(Object.keys(body.cookies).sort(), ['account_id_v2', 'account_mid_v2', 'cookie_token_v2'])
  assert.equal(body.expected_uid, '716004704')
  assert.equal(options.body.includes('do-not-send'), false)
  assert.equal(calls.cookies[0].storeId, 'firefox-container-1')
})
test('cookies from different domains are never combined', async () => {
  const split = fullCookies.map((cookie, i) => ({ ...cookie, domain: i ? '.hoyolab.com' : '.hoyoverse.com' }))
  const { send, calls } = harness({ cookies: split })
  assert.equal((await send()).ok, false)
  assert.equal(calls.requests.length, 0)
})
test('expired and partitioned cookies are not used', async () => {
  for (const extra of [{ expirationDate: 1 }, { partitionKey: { topLevelSite: 'https://other.example' } }]) {
    const { send, calls } = harness({ cookies: fullCookies.map(c => ({ ...c, ...extra })) })
    assert.equal((await send()).ok, false)
    assert.equal(calls.requests.length, 0)
  }
})
