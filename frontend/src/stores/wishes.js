import { defineStore } from 'pinia'
import { getAccountSummary, getAccountStats, getWishes, importWishes } from '../api'

export const useWishStore = defineStore('wishes', {
  state: () => ({
    summary: null,
    stats: null,
    wishes: [],
    wishesTotal: 0,
    loading: false,
    importResult: null,
  }),
  actions: {
    async loadSummary(accountId) {
      this.loading = true
      try {
        this.summary = await getAccountSummary(accountId)
      } catch (e) {
        console.error('Failed to load summary', e)
      } finally {
        this.loading = false
      }
    },
    async loadStats(accountId, gachaType) {
      try {
        this.stats = await getAccountStats(accountId, gachaType)
      } catch (e) {
        console.error('Failed to load stats', e)
      }
    },
    async loadWishes(accountId, params = {}) {
      this.loading = true
      try {
        const result = await getWishes(accountId, params)
        this.wishes = result.items
        this.wishesTotal = result.total
      } catch (e) {
        console.error('Failed to load wishes', e)
      } finally {
        this.loading = false
      }
    },
    async doImport(url, accountName) {
      this.importResult = null
      const result = await importWishes(url, accountName)
      this.importResult = result
      return result
    },
  },
})
