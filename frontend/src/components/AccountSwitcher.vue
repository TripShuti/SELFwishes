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
  border: 1px solid var(--border-strong);
  border-radius: var(--radius);
  padding: 6px 12px;
  font-size: 14px;
  font-family: inherit;
  font-weight: 700;
  cursor: pointer;
  max-width: 220px;
}

.account-select:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(201, 162, 92, 0.25);
}

.no-account {
  font-size: 14px;
}

.text-secondary {
  color: #b9c3d6;
}
</style>
