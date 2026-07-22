<template>
  <div>
    <button class="btn btn-primary" @click="open = true">+ Import</button>

    <div v-if="open" class="modal-overlay" @click.self="close">
      <div class="modal">
        <div class="modal-header">
          <h2>Import Wish History</h2>
          <button class="btn-close" @click="close">&times;</button>
        </div>
        <div class="modal-body">
          <p class="modal-desc">
            Paste your wish history URL below. You can get it from
            <a href="https://paimon.moe/wish/import" target="_blank">this guide</a>.
          </p>

          <div v-if="error" class="alert alert-error">{{ error }}</div>
          <div v-if="result" class="alert alert-success">
            Imported {{ result.new_wishes }} new wishes for {{ result.account_name }}
            (UID: {{ result.uid }})
          </div>

          <div class="form-group">
            <label>Account name (optional)</label>
            <input
              v-model="accountName"
              type="text"
              placeholder="e.g. Main, Alt, Europe..."
              class="input"
            />
          </div>

          <div class="form-group">
            <label>Wish History URL</label>
            <textarea
              v-model="url"
              rows="4"
              placeholder="https://hk4e-api-os.hoyoverse.com/event/gacha_info/api/getGachaLog?authkey=..."
              class="input"
            ></textarea>
          </div>

          <button
            class="btn btn-primary btn-full"
            :disabled="!url || loading"
            @click="doImport"
          >
            {{ loading ? 'Importing...' : 'Import' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { importWishes } from '../api'
import { useAccountStore } from '../stores/accounts'

const emit = defineEmits(['imported'])
const open = ref(false)
const url = ref('')
const accountName = ref('')
const loading = ref(false)
const error = ref('')
const result = ref(null)
const store = useAccountStore()

function close() {
  open.value = false
  url.value = ''
  accountName.value = ''
  error.value = ''
  result.value = null
}

async function doImport() {
  if (!url.value.trim()) return
  loading.value = true
  error.value = ''
  result.value = null

  try {
    const r = await importWishes(url.value.trim(), accountName.value.trim() || undefined)
    result.value = r
    emit('imported', r)
    setTimeout(close, 2500)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Import failed. Check the URL and try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.modal {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  width: 520px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
}

.modal-header h2 {
  font-size: 18px;
  font-weight: 600;
}

.btn-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 24px;
  cursor: pointer;
}

.modal-body {
  padding: 20px;
}

.modal-desc {
  color: var(--text-secondary);
  font-size: 13px;
  margin-bottom: 16px;
  line-height: 1.5;
}

.form-group {
  margin-bottom: 14px;
}

.form-group label {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.input {
  width: 100%;
  background: var(--bg-primary);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 10px 12px;
  color: var(--text-primary);
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
}

.input:focus {
  outline: none;
  border-color: var(--accent);
}

textarea.input {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
}

.btn-full {
  width: 100%;
  justify-content: center;
  margin-top: 8px;
}

.btn-full:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.alert {
  padding: 10px 14px;
  border-radius: var(--radius);
  font-size: 13px;
  margin-bottom: 14px;
}

.alert-error {
  background: rgba(239, 68, 68, 0.15);
  color: var(--red);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.alert-success {
  background: rgba(34, 197, 94, 0.15);
  color: var(--green);
  border: 1px solid rgba(34, 197, 94, 0.3);
}
</style>
