<template>
  <div class="card">
    <div class="table-toolbar">
      <span class="filter-total">{{ wishesTotal }} wishes</span>
    </div>

    <div v-if="!wishes.length && !loading" class="table-empty">No wishes found.</div>
    <template v-else>
      <div :class="['table-wrap', { 'is-loading': loading }]">
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
      </div>
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
  return ts.slice(0, 19).replace('T', ' ')
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
  border-bottom: 2px solid var(--border-strong);
  margin-bottom: 4px;
}

.filter-total {
  font-size: 13px;
  color: var(--text-secondary);
  font-style: italic;
}

.wish-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.wish-table th {
  text-align: left;
  padding: 11px 14px;
  background: linear-gradient(180deg, #ecdcb4 0%, #e3cfa0 100%);
  border: 1px solid #d5c092;
  color: #6a5a3d;
  font-weight: 700;
  font-size: 13px;
  letter-spacing: 0.3px;
  white-space: nowrap;
}

.wish-table th:first-child {
  border-radius: 6px 0 0 6px;
}

.wish-table th:last-child {
  border-radius: 0 6px 6px 0;
}

.sortable {
  cursor: pointer;
  user-select: none;
}

.sortable:hover {
  color: #3e3320;
}

.wish-table td {
  padding: 10px 14px;
  border-bottom: 1px solid var(--border);
  color: #8a8071;
}

.wish-table tbody tr {
  background: #faf5e6;
}

.wish-table tbody tr:nth-child(even) {
  background: #f3ecd7;
}

.wish-table tbody tr:hover {
  background: #eee1bf;
}

.row-5 {
  background: rgba(210, 154, 58, 0.14) !important;
}

.row-5:hover {
  background: rgba(210, 154, 58, 0.22) !important;
}

.row-4 {
  background: rgba(166, 115, 214, 0.1) !important;
}

.row-4:hover {
  background: rgba(166, 115, 214, 0.18) !important;
}

.cell-time {
  color: #988d7a;
  white-space: nowrap;
  font-size: 13px;
}

.cell-item {
  font-weight: 700;
}

.cell-banner {
  font-size: 13px;
  color: var(--text-secondary);
}

.cell-pity {
  text-align: center;
  font-weight: 700;
  color: #6a5a3d;
}

.rarity-5 {
  color: var(--gold);
}

.rarity-4 {
  color: var(--purple);
}

.rarity-3 {
  color: #7f766a;
}

.star-5 {
  color: var(--gold);
}

.star-4 {
  color: var(--purple);
}

.star-3 {
  color: #a29781;
}

.badge {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 10px;
  font-weight: 700;
  border: 1px solid transparent;
}

.badge-win {
  background: rgba(106, 154, 88, 0.15);
  color: #4e7a3d;
  border-color: rgba(106, 154, 88, 0.4);
}

.badge-lose {
  background: rgba(199, 91, 74, 0.13);
  color: #a54434;
  border-color: rgba(199, 91, 74, 0.4);
}

.badge-guarantee {
  background: rgba(74, 144, 217, 0.13);
  color: #35699f;
  border-color: rgba(74, 144, 217, 0.4);
}

.badge-muted {
  background: rgba(150, 138, 115, 0.12);
  color: var(--text-secondary);
  border-color: rgba(150, 138, 115, 0.3);
}

.table-wrap {
  transition: opacity 0.2s ease;
}

.table-wrap.is-loading {
  opacity: 0.45;
  pointer-events: none;
}

.table-loading,
.table-empty {
  padding: 40px;
  text-align: center;
  color: var(--text-secondary);
  font-style: italic;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
  padding: 18px 0 4px 0;
}

.btn-page {
  width: 34px;
  height: 34px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #fbf7ea;
  color: #6a5a3d;
  border: 1px solid var(--border-strong);
  border-radius: 50%;
  font-size: 17px;
  font-family: inherit;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s;
  box-shadow: 0 1px 3px rgba(90, 70, 30, 0.2);
}

.btn-page:hover:not(:disabled) {
  background: linear-gradient(180deg, #e6c88a 0%, #c9a25c 100%);
  border-color: #a8854a;
  color: #3a2f1c;
}

.btn-page:disabled {
  opacity: 0.35;
  cursor: not-allowed;
  box-shadow: none;
}

.page-info {
  font-size: 15px;
  font-weight: 700;
  color: #6a5a3d;
  min-width: 60px;
  text-align: center;
}
</style>
