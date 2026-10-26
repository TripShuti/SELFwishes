<template>
  <div class="account-switcher" v-if="store.hasAccounts">
    <select
      v-model="store.activeAccountId"
      class="account-select"
      aria-label="Active account"
    >
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
  border-radius: 6px;
  padding: 5px 10px;
  font-size: 12px;
  font-family: inherit;
  font-weight: 500;
  cursor: pointer;
  max-width: 230px;
  min-height: 32px;
  width: 100%;
  text-overflow: ellipsis;
}

.account-select:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(201, 162, 92, 0.25);
}

@media (min-width: 601px) and (max-width: 760px) {
  .account-select {
    max-width: 160px;
  }
}

@media (max-width: 600px) {
  .account-select {
    max-width: none;
  }
}

.no-account {
  font-size: 12px;
}

.text-secondary {
  color: #b9c3d6;
}
</style>
