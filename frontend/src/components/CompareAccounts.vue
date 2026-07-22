<template>
  <div class="compare">
    <h2 class="page-title">Compare Accounts</h2>

    <div v-if="store.accounts.length < 2" class="empty-state">
      <p>You need at least 2 accounts to compare.</p>
      <ImportModal @imported="refresh" />
    </div>

    <div v-else>
      <div class="compare-controls">
        <label
          v-for="a in store.accounts"
          :key="a.id"
          class="checkbox-label"
        >
          <input
            type="checkbox"
            :value="a.id"
            v-model="selectedIds"
          />
          {{ a.name }}
        </label>
        <button
          class="btn btn-primary"
          :disabled="selectedIds.length < 2"
          @click="doCompare"
        >
          Compare
        </button>
      </div>

      <div v-if="loading" class="loading">Loading...</div>

      <div v-if="result.length" class="compare-results">
        <table class="compare-table">
          <thead>
            <tr>
              <th>Banner</th>
              <th v-for="r in result" :key="r.account.id">
                {{ r.account.name }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="bannerType in allBannerTypes" :key="bannerType">
              <td class="banner-label">{{ bannerName(bannerType) }}</td>
              <td v-for="r in result" :key="r.account.id" class="banner-cell">
                <template v-if="getBanner(r, bannerType)">
                  <div class="cell-stat">
                    <span class="cell-label">Pulls</span>
                    {{ getBanner(r, bannerType).total_pulls }}
                  </div>
                  <div class="cell-stat">
                    <span class="cell-label gold">5★</span>
                    {{ getBanner(r, bannerType).count_5 }}
                  </div>
                  <div class="cell-stat">
                    <span class="cell-label purple">4★</span>
                    {{ getBanner(r, bannerType).count_4 }}
                  </div>
                </template>
                <span v-else class="no-data">-</span>
              </td>
            </tr>
            <tr class="section-row">
              <td colspan="10">50/50 Stats</td>
            </tr>
            <tr>
              <td class="banner-label">5★ Total</td>
              <td v-for="r in result" :key="r.account.id">
                {{ (r.stats?.wins_5050 || 0) + (r.stats?.losses_5050 || 0) }}
              </td>
            </tr>
            <tr>
              <td class="banner-label">Wins</td>
              <td v-for="r in result" :key="r.account.id">
                {{ r.stats?.wins_5050 || 0 }}
              </td>
            </tr>
            <tr>
              <td class="banner-label">Losses</td>
              <td v-for="r in result" :key="r.account.id">
                {{ r.stats?.losses_5050 || 0 }}
              </td>
            </tr>
            <tr>
              <td class="banner-label">Win Rate</td>
              <td v-for="r in result" :key="r.account.id">
                <template v-if="r.stats?.known_5050">
                  {{ ((r.stats.wins_5050 / r.stats.total_5050) * 100).toFixed(1) }}%
                </template>
                <span v-else class="no-data">-</span>
              </td>
            </tr>
            <tr>
              <td class="banner-label">Avg 5★ Pity</td>
              <td v-for="r in result" :key="r.account.id">
                <template v-if="r.stats?.avg_pity_5 != null">
                  {{ r.stats.avg_pity_5.toFixed(1) }}
                </template>
                <span v-else class="no-data">-</span>
              </td>
            </tr>
            <tr>
              <td class="banner-label">Total Pulls</td>
              <td v-for="r in result" :key="r.account.id">
                {{ r.stats?.total_pulls || 0 }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAccountStore } from '../stores/accounts'
import { compareAccounts } from '../api'
import ImportModal from './ImportModal.vue'

const store = useAccountStore()
const selectedIds = ref(store.accounts.filter((_, i) => i < 3).map(a => a.id))
const loading = ref(false)
const result = ref([])

const allBannerTypes = ['301', '302', '200', '100', '500']

const bannerNames = {
  '100': "Beginners' Wish",
  '200': 'Standard Wish',
  '301': 'Character Event Wish',
  '302': 'Weapon Event Wish',
  '500': 'Chronicled Wish',
}

function bannerName(gt) {
  return bannerNames[gt] || gt
}

function getBanner(accountData, bannerType) {
  return accountData.banners.find((b) => b.gacha_type === bannerType) || null
}

async function doCompare() {
  loading.value = true
  try {
    result.value = await compareAccounts(selectedIds.value)
  } catch (e) {
    console.error('Compare failed', e)
  } finally {
    loading.value = false
  }
}

function refresh() {
  store.loadAccounts()
}
</script>

<style scoped>
.page-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 24px;
}

.compare-controls {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 24px;
  padding: 16px;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  cursor: pointer;
}

.compare-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.compare-table th {
  text-align: left;
  padding: 12px;
  border-bottom: 2px solid var(--border);
  color: var(--text-secondary);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 12px;
  letter-spacing: 0.5px;
}

.compare-table td {
  padding: 12px;
  border-bottom: 1px solid var(--border);
}

.compare-table tbody tr:hover {
  background: var(--bg-hover);
}

.banner-label {
  font-weight: 600;
  white-space: nowrap;
}

.banner-cell {
  min-width: 140px;
}

.cell-stat {
  font-size: 13px;
  margin-bottom: 4px;
}

.cell-label {
  font-size: 11px;
  color: var(--text-secondary);
  margin-right: 4px;
}

.cell-label.gold {
  color: var(--gold);
}

.cell-label.purple {
  color: var(--purple);
}

.section-row td {
  background: var(--bg-card);
  font-weight: 700;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding-top: 20px;
  border-bottom: 2px solid var(--border);
  color: var(--text-primary);
}

.no-data {
  color: var(--text-secondary);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.loading {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}
</style>
