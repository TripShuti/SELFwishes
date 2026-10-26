<template>
  <div class="hoyo-import">
    <div class="hoyo-update-panel">
      <template v-if="!uid && roles.length">
        <label
          >Genshin profile (UID)
          <select v-model="selectedUid" :disabled="busy" class="hoyo-select">
            <option v-for="role in roles" :key="role.uid" :value="role.uid">
              {{ role.nickname || role.uid }} · {{ role.uid }} ·
              {{ role.region }}
            </option>
          </select>
        </label>
      </template>
      <div class="hoyo-actions">
        <button
          class="btn btn-primary"
          :disabled="busy"
          @click="updateFromBrowser"
        >
          {{ busy ? 'Updating…' : 'Update from browser' }}
        </button>
        <button
          v-if="connected"
          class="btn btn-ghost"
          :disabled="busy"
          @click="update()"
        >
          Use saved connection
        </button>
      </div>
      <p class="hoyo-note">
        Sign in to
        <a
          href="https://account.hoyoverse.com/"
          target="_blank"
          rel="noopener noreferrer"
          >HoYoverse</a
        >
        in this browser, then update. Works with a local or remote SELFwishes
        server.
      </p>
      <p v-if="browserBridgeReady" class="hoyo-connected">
        Browser connector ready.
      </p>
      <p v-if="!checking && uid && !connected" class="hoyo-note">
        UID {{ uid }} has no saved connection. Sign in to its HoYoverse account
        and connect from this browser.
      </p>
      <details :open="showSetup" class="hoyo-setup">
        <summary>Set up the browser connector once</summary>
        <p>
          The extension lets this service use your HoYoverse login when you
          click Update from browser. You never need to copy cookies or run a
          terminal command.
        </p>
        <p>
          <a href="/extensions/selfwishes-chromium.zip" download
            >Download for Chrome / Edge / Chromium</a
          ><br />
          Unzip, open the browser's Extensions page, enable Developer mode,
          choose Load unpacked and select the folder.
        </p>
        <p>
          <a href="/extensions/selfwishes-firefox.zip" download
            >Download for Firefox / LibreWolf</a
          ><br />
          Unzip, open <code>about:debugging#/runtime/this-firefox</code>, choose
          Load Temporary Add-on and select manifest.json. This development
          package lasts until the browser restarts; permanent Firefox
          installation requires a Mozilla-signed package.
        </p>
        <p>
          Open this service, click the extension icon and choose
          <strong>Enable for this service</strong>. Then use the button above.
          Only enable a SELFwishes server you trust: it will receive the account
          cookies needed for access.
        </p>
      </details>
    </div>
    <div v-if="message" class="hoyo-result" role="status">
      <strong>{{
        lastResult ? `${lastResult.new_wishes} new wishes` : 'Account connected'
      }}</strong>
      <p>{{ message }}</p>
      <p v-if="lastResult" class="hoyo-result-meta">
        UID {{ lastResult.uid }} · {{ checkedAt }}
      </p>
      <ul v-if="newBanners.length" class="hoyo-result-banners">
        <li v-for="banner in newBanners" :key="banner.gacha_type">
          {{ banner.name }}: +{{ banner.new_count }}
        </li>
      </ul>
    </div>
    <p v-if="error" class="hoyo-error" role="alert">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { getHoyoConnections, importFromHoyo } from '../api'
import { useAccountStore } from '../stores/accounts'
import {
  browserBridgeReady,
  checkBrowserBridge,
  connectBrowser
} from '../services/browserBridge'

const props = defineProps({ uid: { type: String, default: '' } })
const emit = defineEmits(['imported'])
const store = useAccountStore()
const roles = ref([])
const selectedUid = ref('')
const busy = ref(false)
const checking = ref(true)
const showSetup = ref(false)
const error = ref('')
const message = ref('')
const lastResult = ref(null)
const checkedAt = ref('')
const newBanners = computed(() =>
  (lastResult.value?.banners || []).filter((banner) => banner.new_count > 0)
)
const connected = computed(() =>
  roles.value.some((role) => role.uid === (props.uid || selectedUid.value))
)

async function loadConnections() {
  try {
    const data = await getHoyoConnections()
    roles.value = data.roles
    if (!roles.value.some((role) => role.uid === selectedUid.value))
      selectedUid.value = roles.value[0]?.uid || ''
  } catch (e) {
    error.value =
      e.response?.data?.detail || 'Cannot check the HoYoverse connection.'
  } finally {
    checking.value = false
  }
}

onMounted(() => {
  checkBrowserBridge()
  loadConnections()
})
watch(
  () => props.uid,
  () => {
    error.value = ''
    message.value = ''
    lastResult.value = null
    loadConnections()
  }
)

async function performImport(uid) {
  const result = await importFromHoyo(uid)
  await store.loadAccounts()
  store.setActive(result.account_id)
  store.importVersion++
  lastResult.value = result
  checkedAt.value = new Date().toLocaleTimeString()
  message.value = result.new_wishes
    ? `Added ${result.new_wishes} new wishes.`
    : 'History is up to date. No new wishes.'
  emit('imported', result)
}

async function updateFromBrowser() {
  if (busy.value) return
  error.value = ''
  message.value = ''
  lastResult.value = null
  if (!browserBridgeReady.value) {
    checkBrowserBridge()
    showSetup.value = true
    return
  }
  busy.value = true
  try {
    const connected = await connectBrowser(props.uid || undefined)
    await loadConnections()
    showSetup.value = false
    const uid =
      props.uid ||
      (connected.some((role) => role.uid === selectedUid.value)
        ? selectedUid.value
        : connected.length === 1
          ? connected[0].uid
          : null)
    if (uid) await performImport(uid)
    else
      message.value =
        'HoYoverse account connected. Select the Genshin profile (UID) to update.'
  } catch (e) {
    error.value =
      e.response?.data?.detail || e.message || 'Could not connect this browser.'
  } finally {
    busy.value = false
  }
}

async function update() {
  if (busy.value || !connected.value) return
  busy.value = true
  error.value = ''
  message.value = ''
  lastResult.value = null
  try {
    await performImport(props.uid || selectedUid.value)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Update failed. Try again later.'
  } finally {
    busy.value = false
  }
}
</script>

<style scoped>
.hoyo-import {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  width: 100%;
  max-width: 470px;
}
.hoyo-update-panel {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  width: 100%;
  min-width: 0;
}
@media (max-width: 760px) {
  .hoyo-actions {
    width: 100%;
  }
  .hoyo-actions .btn {
    flex: 1 1 160px;
    justify-content: center;
  }
}
.hoyo-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.hoyo-select {
  width: 100%;
  padding: 8px;
  background: var(--bg-input);
  color: var(--text-primary);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius);
  font: inherit;
}
.hoyo-note,
.hoyo-error,
.hoyo-connected,
.hoyo-setup {
  font-size: 13px;
  line-height: 1.5;
}
.hoyo-note {
  color: var(--text-primary);
}
.hoyo-connected {
  color: #3c6830;
}
.hoyo-error {
  color: #a54434;
}
.hoyo-setup {
  padding: 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  width: 100%;
}
.hoyo-setup summary {
  cursor: pointer;
  font-weight: bold;
}
.hoyo-setup p {
  margin-top: 10px;
  overflow-wrap: anywhere;
}
.btn:disabled {
  opacity: 0.6;
  cursor: default;
}

.hoyo-result {
  width: 100%;
  padding: 14px 16px;
  border: 1px solid #90aa79;
  border-left: 4px solid #5a7d3c;
  border-radius: var(--radius);
  background: #edf2df;
  color: #304e24;
  font-size: 14px;
  line-height: 1.5;
}
.hoyo-result strong {
  display: block;
  font-size: 18px;
  margin-bottom: 3px;
}
.hoyo-result-meta {
  margin-top: 5px;
  font-size: 12px;
  color: #52664b;
}
.hoyo-result-banners {
  margin: 8px 0 0;
  padding-left: 18px;
}
</style>
