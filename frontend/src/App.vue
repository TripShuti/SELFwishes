<template>
  <div class="app">
    <header class="header">
      <div class="header-left">
        <router-link to="/dashboard" class="logo">
          <img src="/favicon.gif" class="logo-icon" alt="" /> SELFwishes
        </router-link>
        <nav class="nav">
          <router-link to="/dashboard">Dashboard</router-link>
          <router-link v-if="store.hasAccounts" to="/compare">Compare</router-link>
        </nav>
      </div>
      <div class="header-right">
        <ImportModal @imported="onImported" />
        <AccountSwitcher />
      </div>
    </header>
    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAccountStore } from './stores/accounts'
import AccountSwitcher from './components/AccountSwitcher.vue'
import ImportModal from './components/ImportModal.vue'

const store = useAccountStore()

onMounted(() => {
  store.loadAccounts()
})

function onImported() {
  store.loadAccounts()
}
</script>

<style>
*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --bg-primary: #0f0f1a;
  --bg-secondary: #1a1a2e;
  --bg-card: #222240;
  --bg-hover: #2a2a4a;
  --text-primary: #e0e0f0;
  --text-secondary: #9090b0;
  --accent: #a855f7;
  --accent-hover: #c084fc;
  --gold: #fbbf24;
  --purple: #a855f7;
  --blue: #3b82f6;
  --green: #22c55e;
  --red: #ef4444;
  --border: #2a2a4a;
  --radius: 8px;
  --radius-lg: 12px;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  min-height: 100vh;
}

a {
  color: var(--accent);
  text-decoration: none;
}

.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 32px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: 700;
  color: var(--accent);
  letter-spacing: -0.5px;
}

.logo-icon {
  width: 28px;
  height: 28px;
  border-radius: 4px;
}

.nav {
  display: flex;
  gap: 16px;
}

.nav a {
  color: var(--text-secondary);
  font-size: 14px;
  padding: 4px 8px;
  border-radius: var(--radius);
  transition: all 0.2s;
}

.nav a:hover,
.nav a.router-link-exact-active {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.main {
  flex: 1;
  padding: 24px;
  max-width: 1280px;
  width: 100%;
  margin: 0 auto;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: var(--radius);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--accent);
  color: white;
}

.btn-primary:hover {
  background: var(--accent-hover);
}

.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border);
}

.btn-ghost:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px;
}
</style>
