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
        <div>
          <h1 class="account-title">{{ store.activeAccount.name }}</h1>
          <span class="account-meta">UID: {{ store.activeAccount.uid }}</span>
          <span v-if="store.activeAccount.region" class="account-meta">
            &middot; {{ store.activeAccount.region }}
          </span>
        </div>
        <div class="header-actions">
          <button class="btn btn-ghost" @click="toggleView">
            {{ showTableOnly ? 'Summary View' : 'Table View' }}
          </button>
        </div>
      </div>

      <BannerTabs
        :banners="wishStore.summary?.banners || []"
        :active-tab="activeTab"
        @update:active-tab="onTabChange"
      />

      <div v-if="loading" class="loading">Loading...</div>

      <template v-if="!loading">
        <div v-if="!showTableOnly" class="summary-view">
          <div class="pity-row">
            <PityCard
              v-for="b in visibleBanners"
              :key="b.gacha_type"
              :banner="b"
            />
          </div>

          <StatsPanel :stats="wishStore.stats" />
        </div>

        <div class="wishes-section">
          <h3 class="section-title">
            {{ activeTab === 'all' ? 'All Wishes' : bannerTabName(activeTab) }}
          </h3>
          <WishTable
            :wishes="wishStore.wishes"
            :wishes-total="wishStore.wishesTotal"
            :loading="wishStore.loading"
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
const showTableOnly = ref(false)

const bannerLabels = {
  '100': "Beginners' Wish",
  '200': 'Standard Wish',
  '301': 'Character Event',
  '302': 'Weapon Event',
  '500': 'Chronicled Wish',
}

function bannerTabName(gt) {
  return bannerLabels[gt] || gt
}

const visibleBanners = computed(() => {
  const banners = wishStore.summary?.banners || []
  if (activeTab.value === 'all') return banners
  return banners.filter((b) => b.gacha_type === activeTab.value)
})

function toggleView() {
  showTableOnly.value = !showTableOnly.value
}

function onTabChange(tab) {
  activeTab.value = tab
  loadWishes()
}

async function refresh() {
  if (!store.activeAccountId) return
  activeTab.value = 'all'
  loading.value = true
  await Promise.all([
    wishStore.loadSummary(store.activeAccountId),
    wishStore.loadStats(store.activeAccountId),
  ])
  loadWishes()
  loading.value = false
}

function loadWishes(params = {}) {
  if (!store.activeAccountId) return
  wishStore.loadWishes(store.activeAccountId, {
    sort_by: 'timestamp',
    sort_dir: 'desc',
    ...params,
    gacha_type: params.gacha_type || (activeTab.value !== 'all' ? activeTab.value : undefined),
  })
}

watch(
  () => store.activeAccountId,
  () => refresh(),
  { immediate: true }
)
</script>

<style scoped>
.dashboard {
  min-height: 60vh;
}

.dashboard-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
}

.account-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 4px;
}

.account-meta {
  color: var(--text-secondary);
  font-size: 13px;
  margin-right: 8px;
}

.pity-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.wishes-section {
  margin-top: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state h2 {
  font-size: 20px;
  margin-bottom: 8px;
}

.empty-state p {
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.loading {
  text-align: center;
  padding: 60px;
  color: var(--text-secondary);
}

.header-actions {
  display: flex;
  gap: 8px;
}
</style>
