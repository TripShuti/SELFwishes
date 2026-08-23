import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

export async function fetchAccounts() {
  const { data } = await api.get('/accounts')
  return data
}

export async function createAccount(name, uid, region) {
  const { data } = await api.post('/accounts', { name, uid, region })
  return data
}

export async function deleteAccount(id) {
  await api.delete(`/accounts/${id}`)
}

export async function getAccountSummary(id) {
  const { data } = await api.get(`/accounts/${id}/summary`)
  return data
}

export async function getAccountStats(id, gachaType) {
  const { data } = await api.get(`/accounts/${id}/stats`, {
    params: gachaType ? { gacha_type: gachaType } : {},
  })
  return data
}

export async function getWishes(accountId, params = {}) {
  const { data } = await api.get('/wishes', {
    params: { account_id: accountId, ...params },
  })
  return data
}

export async function importWishes(url, accountName) {
  const { data } = await api.post('/import', { url, account_name: accountName })
  return data
}

export async function compareAccounts(accountIds) {
  const { data } = await api.post('/compare', accountIds)
  return data
}

export async function healthCheck() {
  const { data } = await api.get('/health')
  return data
}
