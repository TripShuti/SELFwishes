<template>
  <div class="card">
    <div class="table-toolbar">
      <span class="filter-total">{{ wishesTotal }} wishes</span>
    </div>

    <div v-if="loading" class="table-loading">Loading...</div>
    <div v-else-if="!wishes.length" class="table-empty">No wishes found.</div>
    <template v-else>
      <table class="wish-table">
        <thead>
          <tr>
            <th @click="sort('timestamp')" class="sortable">
              Time {{ sortIcon('timestamp') }}
            </th>
            <th @click="sort('item_name')" class="sortable">
              Item {{ sortIcon('item_name') }}
            </th>
            <th @click="sort('item_type')" class="sortable">
              Type {{ sortIcon('item_type') }}
            </th>
            <th @click="sort('rarity')" class="sortable">
              Rarity {{ sortIcon('rarity') }}
            </th>
            <th @click="sort('uigf_gacha_type')" class="sortable">
              Banner {{ sortIcon('uigf_gacha_type') }}
            </th>
            <th @click="sort('pity_5')" class="sortable">
              Pity 5★ {{ sortIcon('pity_5') }}
            </th>
            <th @click="sort('pity_4')" class="sortable">
              Pity 4★ {{ sortIcon('pity_4') }}
            </th>
            <th v-if="show5050">
              50/50
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="w in wishes"
            :key="w.id"
            :class="{ 'row-5': w.rarity === 5, 'row-4': w.rarity === 4 }"
          >
            <td class="cell-time">{{ formatTime(w.timestamp) }}</td>
            <td class="cell-item">
              <span :class="rarityClass(w.rarity)">{{ w.item_name }}</span>
            </td>
            <td>{{ w.item_type }}</td>
            <td>
              <span :class="starClass(w.rarity)">{{ '★'.repeat(w.rarity) }}</span>
            </td>
            <td class="cell-banner">{{ bannerName(w.uigf_gacha_type) }}</td>
            <td class="cell-pity">{{ w.pity_5 ?? '-' }}</td>
            <td class="cell-pity">{{ w.pity_4 ?? '-' }}</td>
            <td v-if="show5050">
              <span v-if="w.is_5050_win === true" class="badge badge-win">Win</span>
              <span v-else-if="w.is_5050_win === false" class="badge badge-lose">Lose</span>
              <span v-else-if="w.is_guaranteed === true" class="badge badge-guarantee">Gtd</span>
              <span v-else class="badge badge-muted">-</span>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="pagination" v-if="totalPages > 1">
        <button class="btn-page" :disabled="page <= 1" @click="goTo(page - 1)">‹ Prev</button>
        <span class="page-info">{{ page }} / {{ totalPages }}</span>
        <button class="btn-page" :disabled="page >= totalPages" @click="goTo(page + 1)">Next ›</button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  wishes: { type: Array, default: () => [] },
  wishesTotal: { type: Number, default: 0 },
  loading: { type: Boolean, default: false },
  pageSize: { type: Number, default: 50 },
})

const emit = defineEmits(['load'])

const sortBy = ref('timestamp')
const sortDir = ref('desc')
const page = ref(1)

const totalPages = computed(() => Math.max(1, Math.ceil(props.wishesTotal / props.pageSize)))
const show5050 = computed(() => props.wishes.some((w) => w.uigf_gacha_type === '301'))

const bannerNames = {
  '100': "Beginners' Wish",
  '200': 'Standard Wish',
  '301': 'Character Event',
  '302': 'Weapon Event',
  '500': 'Chronicled Wish',
}

function bannerName(gt) {
  return bannerNames[gt] || gt
}

function sort(field) {
  if (sortBy.value === field) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = field
    sortDir.value = 'asc'
  }
  emitLoad()
}

function sortIcon(field) {
  if (sortBy.value !== field) return '↕'
  return sortDir.value === 'asc' ? '↑' : '↓'
}

function formatTime(ts) {
  if (!ts) return '-'
  return ts.slice(0, 16).replace('T', ' ')
}

function goTo(p) {
  page.value = p
  emitLoad()
}

function emitLoad() {
  emit('load', {
    sort_by: sortBy.value,
    sort_dir: sortDir.value,
    page: page.value,
    size: props.pageSize,
  })
}

function rarityClass(r) {
  if (r === 5) return 'rarity-5'
  if (r === 4) return 'rarity-4'
  return 'rarity-3'
}

function starClass(r) {
  if (r === 5) return 'star-5'
  if (r === 4) return 'star-4'
  return 'star-3'
}
</script>

<style scoped>
.table-toolbar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 0 12px 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 4px;
}

.filter-total {
  font-size: 12px;
  color: var(--text-secondary);
}

.wish-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.wish-table th {
  text-align: left;
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.sortable {
  cursor: pointer;
  user-select: none;
}

.sortable:hover {
  color: var(--text-primary);
}

.wish-table td {
  padding: 8px 12px;
  border-bottom: 1px solid rgba(42, 42, 74, 0.5);
}

.wish-table tr:hover {
  background: var(--bg-hover);
}

.row-5 {
  background: rgba(251, 191, 36, 0.06) !important;
}

.row-5:hover {
  background: rgba(251, 191, 36, 0.1) !important;
}

.row-4 {
  background: rgba(168, 85, 247, 0.04) !important;
}

.cell-time {
  color: var(--text-secondary);
  white-space: nowrap;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
}

.cell-item {
  font-weight: 500;
}

.cell-banner {
  font-size: 12px;
  color: var(--text-secondary);
}

.cell-pity {
  font-family: 'SF Mono', 'Fira Code', monospace;
  text-align: center;
}

.rarity-5 {
  color: var(--gold);
}

.rarity-4 {
  color: var(--purple);
}

.rarity-3 {
  color: #6b7280;
}

.star-5 {
  color: var(--gold);
}

.star-4 {
  color: var(--purple);
}

.star-3 {
  color: #6b7280;
}

.badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 600;
}

.badge-win {
  background: rgba(34, 197, 94, 0.15);
  color: var(--green);
}

.badge-lose {
  background: rgba(239, 68, 68, 0.15);
  color: var(--red);
}

.badge-guarantee {
  background: rgba(59, 130, 246, 0.15);
  color: var(--blue);
}

.badge-muted {
  background: rgba(144, 144, 176, 0.1);
  color: var(--text-secondary);
}

.table-loading,
.table-empty {
  padding: 40px;
  text-align: center;
  color: var(--text-secondary);
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 16px 0 0 0;
  border-top: 1px solid var(--border);
  margin-top: 4px;
}

.btn-page {
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 6px 14px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-page:hover:not(:disabled) {
  background: var(--bg-hover);
  border-color: var(--accent);
}

.btn-page:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  font-size: 13px;
  color: var(--text-secondary);
  font-family: 'SF Mono', 'Fira Code', monospace;
}
</style>
