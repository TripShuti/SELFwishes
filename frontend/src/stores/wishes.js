import { defineStore } from 'pinia'
import {
  getAccountSummary,
  getAccountStats,
  getWishes,
  importWishes
} from '../api'

export const useWishStore = defineStore('wishes', {
  state: () => ({
    summary: null,
    stats: null,
    wishes: [],
    wishesTotal: 0,
    loading: false,
    importResult: null,
    wishesError: '',
    wishesRequest: 0
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
      const request = ++this.wishesRequest
      this.loading = true
      this.wishesError = ''
      try {
        const result = await getWishes(accountId, params)
        if (request !== this.wishesRequest) return
        this.wishes = result.items
        this.wishesTotal = result.total
      } catch (e) {
        if (request !== this.wishesRequest) return
        this.wishes = []
        this.wishesTotal = 0
        this.wishesError = 'Could not load wish history. Please try again.'
        console.error('Failed to load wishes', e)
      } finally {
        if (request === this.wishesRequest) this.loading = false
      }
    },
    async doImport(url, accountName) {
      this.importResult = null
      const result = await importWishes(url, accountName)
      this.importResult = result
      return result
    }
  }
})
