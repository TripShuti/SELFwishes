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
  background: rgba(25, 38, 60, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.modal {
  background: var(--bg-card);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg);
  box-shadow:
    0 0 0 3px rgba(58, 74, 107, 0.5),
    0 10px 40px rgba(20, 32, 55, 0.5);
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
  border-bottom: 2px solid var(--border-strong);
  background: linear-gradient(180deg, #ecdcb4 0%, #e3cfa0 100%);
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}

.modal-header h2 {
  font-size: 19px;
  font-weight: 700;
  color: #6a5a3d;
}

.btn-close {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #fbf7ea;
  border: 1px solid var(--border-strong);
  color: #6a5a3d;
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-close:hover {
  background: linear-gradient(180deg, #e6c88a 0%, #c9a25c 100%);
  color: #3a2f1c;
}

.modal-body {
  padding: 20px;
}

.modal-desc {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 16px;
  line-height: 1.5;
  font-style: italic;
}

.form-group {
  margin-bottom: 14px;
}

.form-group label {
  display: block;
  font-size: 14px;
  color: var(--heading);
  font-weight: 700;
  margin-bottom: 5px;
}

.input {
  width: 100%;
  background: var(--bg-input);
  border: 1px solid var(--border-strong);
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
  box-shadow: 0 0 0 3px rgba(201, 162, 92, 0.25);
}

textarea.input {
  font-size: 13px;
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
  font-size: 14px;
  margin-bottom: 14px;
  border: 1px solid transparent;
}

.alert-error {
  background: rgba(199, 91, 74, 0.12);
  color: #a54434;
  border-color: rgba(199, 91, 74, 0.4);
}

.alert-success {
  background: rgba(106, 154, 88, 0.13);
  color: #4e7a3d;
  border-color: rgba(106, 154, 88, 0.4);
}
</style>
