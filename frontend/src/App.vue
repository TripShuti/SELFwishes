<template>
  <div class="app">
    <header class="header">
      <div class="header-left">
        <router-link
          to="/dashboard"
          class="logo"
          aria-label="SELFwishes dashboard"
        >
          <span class="logo-gem" aria-hidden="true">
            <img
              class="logo-art"
              src="/brand/primogem.png"
              width="64"
              height="64"
              alt=""
              fetchpriority="high"
            />
            <span class="primogem-glint"></span>
          </span>
          <span class="logo-wordmark">SELF<span>wishes</span></span>
        </router-link>
        <nav class="nav">
          <router-link to="/dashboard">Dashboard</router-link>
          <router-link v-if="store.hasAccounts" to="/compare"
            >Compare</router-link
          >
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
    <footer class="app-footer">
      <strong>SELFwishes</strong><span>Your wishes, your server.</span>
    </footer>
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
@font-face {
  font-family: 'SELFwishes Philosopher';
  src: url('/fonts/philosopher/Philosopher-Bold.ttf') format('truetype');
  font-style: normal;
  font-weight: 700;
  font-display: swap;
}
*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
:root {
  font-family:
    Inter,
    ui-sans-serif,
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    sans-serif;
  --bg-primary: #edf5fa;
  --bg-secondary: #243953;
  --bg-card: #fffefa;
  --bg-card-alt: #f6f5f0;
  --bg-hover: #f0f4f7;
  --bg-input: #ffffff;
  --text-primary: #293b52;
  --text-secondary: #64748b;
  --heading: #182b46;
  --accent: #c4a062;
  --accent-hover: #ae894b;
  --gold: #9e691b;
  --purple: #7950ad;
  --blue: #4686bd;
  --green: #397452;
  --red: #b64c47;
  --border: #e5e8eb;
  --border-strong: #d4dce2;
  --frame: #243953;
  --radius: 8px;
  --radius-lg: 14px;
  color-scheme: light;
}
body {
  background:
    radial-gradient(ellipse at 15% 0, #dceef9, transparent 55%),
    linear-gradient(160deg, #f1f7fb, #edf4f8);
  background-attachment: fixed;
  color: var(--text-primary);
  min-height: 100vh;
  font-size: 14px;
  line-height: 1.5;
}
a {
  color: #8a642a;
  text-decoration: none;
}
a:hover {
  text-decoration: underline;
}
button,
input,
select,
textarea {
  font: inherit;
}
button,
select {
  touch-action: manipulation;
}
button {
  cursor: pointer;
}
button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}
:focus-visible {
  outline: 3px solid #5999d0;
  outline-offset: 3px;
}
h1,
h2,
h3 {
  color: var(--heading);
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
  gap: 16px;
  padding: 8px max(20px, calc((100vw - 1376px) / 2));
  background: #243953;
  border-bottom: 1px solid #c4a062;
}
.header-left,
.header-right,
.nav,
.logo {
  display: flex;
  align-items: center;
}
.header-left {
  gap: 14px;
  min-width: 0;
}
.header-right {
  gap: 8px;
  min-width: 0;
}
.logo {
  height: 32px;
  flex: 0 0 auto;
  gap: 5px;
  border-radius: 4px;
  white-space: nowrap;
}
.logo-gem {
  position: relative;
  display: block;
  width: 32px;
  height: 32px;
  flex: 0 0 32px;
}
.logo-wordmark {
  font-family: 'SELFwishes Philosopher', Georgia, serif;
  font-weight: 700;
  font-size: 23px;
  line-height: 1;
  letter-spacing: 0.15px;
  color: #f4ead7;
}
.logo-wordmark > span {
  color: #d8e4ef;
}
.logo-art {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.primogem-glint {
  position: absolute;
  left: 64%;
  top: 30%;
  width: 10px;
  height: 10px;
  opacity: 0;
  pointer-events: none;
  transform: translate(-50%, -50%) scale(0.5);
  animation: primogem-sparkle 6s ease-in-out infinite;
}
.primogem-glint::before,
.primogem-glint::after {
  content: '';
  position: absolute;
  left: 50%;
  top: 50%;
  border-radius: 50%;
  background: #fff;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 6px 2px #b8e5ffb3;
}
.primogem-glint::before {
  width: 2px;
  height: 100%;
}
.primogem-glint::after {
  width: 100%;
  height: 2px;
}
@keyframes primogem-sparkle {
  0%,
  82%,
  100% {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.4) rotate(0deg);
  }
  88% {
    opacity: 0.95;
    transform: translate(-50%, -50%) scale(1.1) rotate(12deg);
  }
  94% {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.65) rotate(24deg);
  }
}
.logo:hover {
  text-decoration: none;
}
.nav {
  gap: 4px;
}
.nav a {
  color: #cbd7e4;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}
.nav a:hover {
  background: #ffffff12;
  text-decoration: none;
}
.nav a.router-link-exact-active {
  color: #f8e7c4;
  background: #ffffff12;
  box-shadow: inset 0 -2px var(--accent);
}
.header-right > :first-child > .btn {
  min-height: 32px;
  padding: 5px 11px;
  font-size: 12px;
  border-radius: 6px;
}
.header-right > :first-child > .btn-primary {
  background: #eddbb7;
  border-color: #eddbb7;
  color: #263953;
  box-shadow: none;
}
.main {
  flex: 1;
  padding: 32px 24px;
  max-width: 1424px;
  width: 100%;
  margin: 0 auto;
}
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 42px;
  padding: 9px 16px;
  border: 1px solid transparent;
  border-radius: var(--radius);
  font-weight: 600;
  line-height: 1.4;
  transition: background 0.15s;
}
.btn-primary {
  background: #243953;
  color: #fff;
  border-color: #243953;
}
.btn-primary:hover:not(:disabled) {
  background: #365274;
}
.btn-ghost {
  background: var(--bg-card);
  color: var(--text-primary);
  border-color: var(--border-strong);
}
.btn-ghost:hover:not(:disabled) {
  background: var(--bg-hover);
}
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: 0 3px 12px #20395205;
  padding: 22px;
}
.app-footer {
  max-width: 1424px;
  width: 100%;
  margin: 0 auto;
  padding: 0 24px 24px;
  display: flex;
  gap: 12px;
  color: var(--text-secondary);
  font-size: 12px;
}
.app-footer strong {
  font-family: Georgia, serif;
}
@media (prefers-reduced-motion: reduce) {
  .primogem-glint {
    animation: none;
    display: none;
  }
  *,
  *::before,
  *::after {
    transition: none !important;
    scroll-behavior: auto !important;
  }
}
@media (max-width: 760px) {
  .header {
    padding: 8px 12px;
    gap: 10px;
  }
  .header-left {
    gap: 8px;
  }
  .logo-wordmark {
    font-size: 20px;
  }
  .nav a {
    padding: 6px 8px;
  }
  .main {
    padding: 24px 16px;
  }
  .card {
    padding: 16px;
  }
  .app-footer {
    padding: 0 16px 20px;
  }
}
@media (max-width: 600px) {
  .header {
    flex-wrap: wrap;
    padding: 6px 12px;
    gap: 6px;
  }
  .header-left {
    width: 100%;
    justify-content: space-between;
  }
  .logo {
    height: 30px;
    gap: 3px;
  }
  .logo-gem {
    width: 30px;
    height: 30px;
    flex-basis: 30px;
  }
  .logo-wordmark {
    font-size: 20px;
    letter-spacing: 0;
  }
  .header-right {
    width: 100%;
  }
  .header-right > :first-child {
    flex-shrink: 0;
  }
  .header-right > :last-child {
    flex: 1;
    min-width: 0;
  }
}
@media (max-width: 360px) {
  .logo-wordmark {
    font-size: 18px;
  }
  .logo {
    gap: 1px;
  }
  .header-left {
    gap: 4px;
  }
  .nav {
    gap: 0;
  }
  .nav a {
    padding-inline: 6px;
  }
}
</style>
