<template>
  <div class="account-switcher" v-if="store.hasAccounts">
    <select v-model="store.activeAccountId" class="account-select">
      <option v-for="a in store.accounts" :key="a.id" :value="a.id">
        {{ a.name }} ({{ a.uid || 'no UID' }})
      </option>
    </select>
  </div>
  <div v-else class="no-account">
    <span class="text-secondary">No accounts</span>
  </div>
</template>

<script setup>
import { useAccountStore } from '../stores/accounts'

const store = useAccountStore()
</script>

<style scoped>
.account-select {
  background: var(--bg-card);
  color: var(--text-primary);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 6px 12px;
  font-size: 13px;
  cursor: pointer;
  max-width: 200px;
}

.account-select:focus {
  outline: none;
  border-color: var(--accent);
}

.no-account {
  font-size: 13px;
}

.text-secondary {
  color: var(--text-secondary);
}
</style>
