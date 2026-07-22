import { defineStore } from 'pinia'
import { fetchAccounts, createAccount, deleteAccount } from '../api'

export const useAccountStore = defineStore('accounts', {
  state: () => ({
    accounts: [],
    activeAccountId: null,
    loading: false,
  }),
  getters: {
    activeAccount: (state) =>
      state.accounts.find((a) => a.id === state.activeAccountId) || null,
    hasAccounts: (state) => state.accounts.length > 0,
  },
  actions: {
    async loadAccounts() {
      this.loading = true
      try {
        this.accounts = await fetchAccounts()
        if (!this.activeAccountId && this.accounts.length > 0) {
          this.activeAccountId = this.accounts[0].id
        } else if (this.accounts.length === 0) {
          this.activeAccountId = null
        } else if (!this.accounts.find((a) => a.id === this.activeAccountId)) {
          this.activeAccountId = this.accounts[0].id
        }
      } catch (e) {
        console.error('Failed to load accounts', e)
      } finally {
        this.loading = false
      }
    },
    async addAccount(name, uid, region) {
      const acct = await createAccount(name, uid, region)
      this.accounts.push(acct)
      this.activeAccountId = acct.id
      return acct
    },
    async removeAccount(id) {
      await deleteAccount(id)
      this.accounts = this.accounts.filter((a) => a.id !== id)
      if (this.activeAccountId === id) {
        this.activeAccountId = this.accounts[0]?.id || null
      }
    },
    setActive(id) {
      this.activeAccountId = id
    },
  },
})
