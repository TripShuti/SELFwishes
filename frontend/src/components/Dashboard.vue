<template>
  <div class="dashboard">
    <div v-if="!store.activeAccount" class="empty-state">
      <div class="empty-icon">🎯</div>
      <h2>No accounts yet</h2>
      <p>Import your Genshin Impact wish history to get started.</p>
      <ImportModal @imported="refresh" />
    </div>

    <template v-else>
      <div class="dashboard-header">
        <div class="account-heading">
          <h1 class="account-name">{{ store.activeAccount.name }}</h1>
          <span class="account-meta">UID: {{ store.activeAccount.uid }}</span>
          <span v-if="store.activeAccount.region" class="account-meta">
            &middot; {{ store.activeAccount.region }}
          </span>
        </div>
      </div>

      <StatsPanel v-if="!loading" :stats="wishStore.stats" />

      <BannerTabs
        :banners="wishStore.summary?.banners || []"
        :active-tab="activeTab"
        @update:active-tab="onTabChange"
      />

      <div v-if="loading" class="loading">Loading...</div>

      <template v-if="!loading">
        <div class="pity-row">
          <PityCard
            v-for="b in visibleBanners"
            :key="b.gacha_type"
            :banner="b"
          />
        </div>

        <div class="wishes-section">
          <WishTable
            :key="`${store.activeAccountId}-${activeTab}-${store.importVersion}`"
            :title="
              activeTab === 'all' ? 'Wish history' : bannerTabName(activeTab)
            "
            :wishes="wishStore.wishes"
            :wishes-total="wishStore.wishesTotal"
            :loading="wishStore.loading"
            :error="wishStore.wishesError"
            @load="loadWishes"
          />
        </div>
      </template>
    </template>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useAccountStore } from '../stores/accounts'
import { useWishStore } from '../stores/wishes'
import ImportModal from './ImportModal.vue'
import BannerTabs from './BannerTabs.vue'
import PityCard from './PityCard.vue'
import WishTable from './WishTable.vue'
import StatsPanel from './StatsPanel.vue'

const store = useAccountStore()
const wishStore = useWishStore()
const loading = ref(false)
const activeTab = ref('all')

const bannerLabels = {
  100: "Beginners' Wish",
  200: 'Standard Wish',
  301: 'Character Event',
  302: 'Weapon Event',
  500: 'Chronicled Wish'
}

function bannerTabName(gt) {
  return bannerLabels[gt] || gt
}

const visibleBanners = computed(() => {
  const banners = wishStore.summary?.banners || []
  if (activeTab.value === 'all') return banners
  return banners.filter((b) => b.gacha_type === activeTab.value)
})

function onTabChange(tab) {
  activeTab.value = tab
  loadStats()
  loadWishes()
}

async function refresh() {
  if (!store.activeAccountId) return
  activeTab.value = 'all'
  loading.value = true
  await Promise.all([wishStore.loadSummary(store.activeAccountId), loadStats()])
  loadWishes()
  loading.value = false
}

function loadStats() {
  if (!store.activeAccountId) return Promise.resolve()
  const gt = activeTab.value !== 'all' ? activeTab.value : undefined
  return wishStore.loadStats(store.activeAccountId, gt)
}

function loadWishes(params = {}) {
  if (!store.activeAccountId) return
  wishStore.loadWishes(store.activeAccountId, {
    sort_by: 'timestamp',
    sort_dir: 'desc',
    ...params,
    gacha_type:
      params.gacha_type ||
      (activeTab.value !== 'all' ? activeTab.value : undefined)
  })
}

watch(
  () => [store.activeAccountId, store.importVersion],
  () => refresh(),
  { immediate: true }
)
</script>

<style scoped>
.dashboard-header {
  margin-bottom: 20px;
}
.account-heading {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 4px 12px;
  min-width: 0;
}
.account-name {
  font-size: 18px;
  font-weight: 650;
  overflow-wrap: anywhere;
}
.account-meta {
  font-size: 12px;
  color: var(--text-secondary);
}
.pity-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(225px, 1fr));
  gap: 16px;
}
.wishes-section {
  margin-top: 24px;
}
.empty-state {
  text-align: center;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 80px 20px;
}
.empty-state h2 {
  font:
    700 28px Georgia,
    serif;
  margin-bottom: 12px;
}
.empty-state p {
  color: var(--text-secondary);
  margin-bottom: 24px;
}
.empty-icon {
  font-size: 48px;
  margin-bottom: 20px;
}
.loading {
  text-align: center;
  padding: 60px;
  color: var(--text-secondary);
}
@media (max-width: 760px) {
  .pity-row {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
  }
}
@media (max-width: 360px) {
  .pity-row {
    grid-template-columns: 1fr;
  }
}
</style>
