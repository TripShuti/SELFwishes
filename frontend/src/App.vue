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
  --sky-top: #a5d2f2;
  --sky-bottom: #c9e4f7;
  --bg-primary: #9cc8ec;
  --bg-secondary: #2b3a57;
  --bg-card: #f7f1df;
  --bg-card-alt: #f1e8d0;
  --bg-hover: #efe3c6;
  --bg-input: #fbf7ea;
  --text-primary: #5b5142;
  --text-secondary: #9a8f7b;
  --heading: #4a4133;
  --accent: #c9a25c;
  --accent-hover: #d8b56e;
  --gold: #d29a3a;
  --purple: #a673d6;
  --blue: #4a90d9;
  --green: #6a9a58;
  --red: #c75b4a;
  --border: #ddcfa8;
  --border-strong: #c2ab7c;
  --frame: #3a4a6b;
  --radius: 6px;
  --radius-lg: 10px;
}

body {
  font-family: Georgia, 'Palatino Linotype', 'Book Antiqua', 'Times New Roman', serif;
  background:
    radial-gradient(ellipse 80% 50% at 20% 0%, rgba(255, 255, 255, 0.55), transparent 60%),
    radial-gradient(ellipse 70% 45% at 85% 15%, rgba(255, 255, 255, 0.45), transparent 55%),
    radial-gradient(ellipse 90% 60% at 50% 110%, rgba(255, 255, 255, 0.35), transparent 60%),
    linear-gradient(180deg, var(--sky-top) 0%, var(--sky-bottom) 100%);
  background-attachment: fixed;
  color: var(--text-primary);
  min-height: 100vh;
}

a {
  color: #8a6a2f;
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
  background: linear-gradient(180deg, #33445f 0%, #263450 100%);
  border-bottom: 2px solid var(--accent);
  box-shadow: 0 2px 12px rgba(30, 42, 66, 0.4);
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
  color: #e8d5a8;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
}

.logo-icon {
  width: 28px;
  height: 28px;
  border-radius: 4px;
}

.nav {
  display: flex;
  gap: 8px;
}

.nav a {
  color: #b9c3d6;
  font-size: 14px;
  padding: 5px 12px;
  border-radius: var(--radius);
  border: 1px solid transparent;
  transition: all 0.2s;
}

.nav a:hover {
  color: #e8d5a8;
  background: rgba(232, 213, 168, 0.08);
}

.nav a.router-link-exact-active {
  color: #3a2f1c;
  background: linear-gradient(180deg, #e6c88a 0%, #c9a25c 100%);
  border-color: #a8854a;
  font-weight: 700;
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
  padding: 8px 18px;
  border: 1px solid #a8854a;
  border-radius: var(--radius);
  font-size: 14px;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(180deg, #e6c88a 0%, #c9a25c 100%);
  color: #3a2f1c;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.5), 0 1px 3px rgba(90, 70, 30, 0.3);
}

.btn-primary:hover {
  background: linear-gradient(180deg, #f0d69c 0%, #d8b56e 100%);
}

.btn-ghost {
  background: var(--bg-card);
  color: var(--text-primary);
  border-color: var(--border-strong);
}

.btn-ghost:hover {
  background: var(--bg-hover);
}

.card {
  background: var(--bg-card);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg);
  box-shadow:
    0 0 0 3px rgba(58, 74, 107, 0.35),
    0 4px 16px rgba(40, 55, 85, 0.25);
  padding: 20px;
}

@media (max-width: 720px) {
  .header {
    flex-wrap: wrap;
    gap: 10px;
    padding: 10px 14px;
  }

  .header-left {
    width: 100%;
    justify-content: space-between;
    gap: 12px;
  }

  .logo {
    font-size: 17px;
  }

  .logo-icon {
    width: 22px;
    height: 22px;
  }

  .nav {
    gap: 4px;
  }

  .nav a {
    font-size: 13px;
    padding: 4px 10px;
  }

  .header-right {
    width: 100%;
    justify-content: space-between;
    gap: 8px;
  }

  .main {
    padding: 12px;
  }

  .card {
    padding: 14px;
  }
}
</style>
