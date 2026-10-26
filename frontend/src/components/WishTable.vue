<template>
  <section class="card history" :aria-busy="loading">
    <div class="table-toolbar">
      <div class="history-heading">
        <h2>{{ title }}</h2>
        <span class="filter-total"
          >{{ wishesTotal.toLocaleString() }} wishes</span
        >
      </div>
      <div class="table-filters">
        <label class="search-field"
          ><span aria-hidden="true">⌕</span
          ><input
            v-model="search"
            type="search"
            aria-label="Search items in wish history"
            placeholder="Search items…"
            maxlength="120"
        /></label>
        <select
          v-model="rarity"
          aria-label="Filter by rarity"
          @change="filterChanged"
        >
          <option value="">All rarities</option>
          <option value="5">5★</option>
          <option value="4">4★</option>
          <option value="3">3★</option>
        </select>
      </div>
    </div>
    <div class="mobile-sort">
      <label
        >Sort by
        <select :value="`${sortBy}:${sortDir}`" @change="changeMobileSort">
          <option value="timestamp:desc">Newest first</option>
          <option value="timestamp:asc">Oldest first</option>
          <option value="rarity:desc">Highest rarity</option>
          <option value="item_name:asc">Item name</option>
          <option value="pity_5:desc">Highest 5★ pity</option>
        </select></label
      >
    </div>
    <div v-if="error" class="table-empty" role="alert">
      {{ error }} <button class="btn btn-ghost" @click="emitLoad">Retry</button>
    </div>
    <div v-else-if="!wishes.length && !loading" class="table-empty">
      No wishes found. Try another search or rarity.
    </div>
    <div v-else-if="!wishes.length" class="table-empty" role="status">
      Loading wish history…
    </div>
    <div v-else :class="['table-wrap', { 'is-loading': loading }]">
      <table class="wish-table">
        <thead>
          <tr>
            <th
              v-for="column in columns"
              :key="column.key"
              :aria-sort="
                sortBy === column.key
                  ? sortDir === 'asc'
                    ? 'ascending'
                    : 'descending'
                  : 'none'
              "
            >
              <button @click="sort(column.key)">
                {{ column.label }}
                <span aria-hidden="true">{{ sortIcon(column.key) }}</span>
              </button>
            </th>
            <th v-if="show5050">50/50</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="w in wishes" :key="w.id" :class="[`row-${w.rarity}`]">
            <td class="cell-item" data-label="Item">
              <div class="item-content">
                <ItemIcon
                  :item-id="w.item_id"
                  :name="w.item_name"
                  :item-type="w.item_type"
                  :rarity="w.rarity"
                />
                <div>
                  <span :class="`rarity-${w.rarity}`" class="item-name">{{
                    w.item_name
                  }}</span
                  ><span class="item-type">{{ w.item_type }}</span>
                </div>
              </div>
            </td>
            <td class="cell-banner" data-label="Banner">
              {{ bannerName(w.uigf_gacha_type) }}
            </td>
            <td class="cell-rarity" data-label="Rarity">
              <span
                :class="`stars-${w.rarity}`"
                :aria-label="`${w.rarity} stars`"
                >{{ '★'.repeat(w.rarity) }}</span
              >
            </td>
            <td class="cell-pity" data-label="5★ pity">
              {{ w.pity_5 ?? '—' }}
            </td>
            <td class="cell-pity" data-label="4★ pity">
              {{ w.pity_4 ?? '—' }}
            </td>
            <td class="cell-time" data-label="Date">
              {{ formatTime(w.timestamp) }}
            </td>
            <td v-if="show5050" class="cell-result" data-label="50/50">
              <span v-if="w.is_5050_win === true" class="badge badge-win"
                >Win</span
              ><span
                v-else-if="w.is_5050_win === false"
                class="badge badge-lose"
                >Lost</span
              ><span
                v-else-if="w.is_guaranteed === true"
                class="badge badge-guarantee"
                >Guaranteed</span
              ><span v-else class="badge-muted">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="pagination">
      <span class="pagination-count"
        >{{ wishesTotal ? (page - 1) * pageSize + 1 : 0 }}–{{
          Math.min(page * pageSize, wishesTotal)
        }}
        of {{ wishesTotal.toLocaleString() }}</span
      >
      <div class="page-controls">
        <button
          class="btn-page"
          :disabled="page <= 1 || loading"
          @click="goTo(page - 1)"
          aria-label="Previous page"
        >
          ‹</button
        ><span class="page-info">{{ page }} / {{ totalPages }}</span
        ><button
          class="btn-page"
          :disabled="page >= totalPages || loading"
          @click="goTo(page + 1)"
          aria-label="Next page"
        >
          ›
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, watch, onBeforeUnmount } from 'vue'
import ItemIcon from './ItemIcon.vue'
const props = defineProps({
  error: { type: String, default: '' },
  wishes: { type: Array, default: () => [] },
  wishesTotal: { type: Number, default: 0 },
  loading: { type: Boolean, default: false },
  pageSize: { type: Number, default: 50 },
  title: { type: String, default: 'Wish history' }
})
const emit = defineEmits(['load'])
const sortBy = ref('timestamp'),
  sortDir = ref('desc'),
  page = ref(1),
  search = ref(''),
  rarity = ref('')
const columns = [
  { key: 'item_name', label: 'Item' },
  { key: 'uigf_gacha_type', label: 'Banner' },
  { key: 'rarity', label: 'Rarity' },
  { key: 'pity_5', label: '5★ pity' },
  { key: 'pity_4', label: '4★ pity' },
  { key: 'timestamp', label: 'Date' }
]
const totalPages = computed(() =>
  Math.max(1, Math.ceil(props.wishesTotal / props.pageSize))
)
const show5050 = computed(() =>
  props.wishes.some((w) => w.uigf_gacha_type === '301')
)
const bannerNames = {
  100: 'Beginners',
  200: 'Standard Wish',
  301: 'Character Event',
  302: 'Weapon Event',
  500: 'Chronicled Wish'
}
const bannerName = (gt) => bannerNames[gt] || gt
let searchTimer
watch(search, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(filterChanged, 300)
})
onBeforeUnmount(() => clearTimeout(searchTimer))
function filterChanged() {
  clearTimeout(searchTimer)
  page.value = 1
  emitLoad()
}
function sort(field) {
  sortDir.value =
    sortBy.value === field && sortDir.value === 'asc' ? 'desc' : 'asc'
  sortBy.value = field
  page.value = 1
  emitLoad()
}
function changeMobileSort(event) {
  ;[sortBy.value, sortDir.value] = event.target.value.split(':')
  page.value = 1
  emitLoad()
}
function sortIcon(field) {
  return sortBy.value === field ? (sortDir.value === 'asc' ? '↑' : '↓') : '↕'
}
function formatTime(ts) {
  return ts ? ts.slice(0, 19).replace('T', ' ') : '—'
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
    search: search.value.trim() || undefined,
    rarity: rarity.value || undefined
  })
}
</script>

<style scoped>
.history {
  padding: 0;
  overflow: hidden;
}
.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 22px;
  flex-wrap: wrap;
}
.history-heading {
  display: flex;
  align-items: baseline;
  gap: 12px;
}
.history-heading h2 {
  font:
    700 23px Georgia,
    serif;
}
.filter-total {
  font-size: 12px;
  color: var(--text-secondary);
}
.table-filters {
  display: flex;
  gap: 10px;
}
.search-field {
  display: flex;
  align-items: center;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius);
  padding-left: 12px;
  background: #fff;
}
.search-field > span {
  font-size: 24px;
  line-height: 1;
  color: var(--text-secondary);
}
.search-field input {
  border: 0;
  background: transparent;
  min-width: 0;
  width: 190px;
  padding: 10px;
  color: var(--text-primary);
  border-radius: var(--radius);
}
select {
  min-height: 42px;
  padding: 8px 12px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius);
  color: var(--text-primary);
  background: white;
}
.table-wrap {
  overflow-x: auto;
  transition: opacity 0.15s;
}
.table-wrap.is-loading {
  opacity: 0.45;
  pointer-events: none;
}
.wish-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 13px;
}
.wish-table th {
  padding: 12px 18px;
  background: #f6f6f2;
  font-size: 11px;
  font-weight: 600;
  color: #56667b;
  white-space: nowrap;
  border-block: 1px solid var(--border);
}
.wish-table th button {
  background: none;
  border: 0;
  font: inherit;
  color: inherit;
  text-align: left;
  min-height: 24px;
}
.wish-table th button span {
  margin-left: 5px;
  color: #8793a4;
}
.wish-table td {
  padding: 10px 18px;
  border-bottom: 1px solid var(--border);
}
.wish-table tbody tr:hover {
  background: #edf4f9;
}
.row-5 {
  background: #fbf5e9;
}
.row-4 {
  background: #f6f1fa;
}
.item-content {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 180px;
}
.item-name {
  font-weight: 600;
  color: var(--heading);
}
.item-type {
  display: block;
  color: var(--text-secondary);
  font-size: 10px;
  margin-top: 2px;
}
.rarity-5,
.stars-5 {
  color: var(--gold);
}
.rarity-4,
.stars-4 {
  color: var(--purple);
}
.stars-3 {
  color: #71879f;
}
.cell-time,
.cell-banner {
  font-size: 11px;
  color: var(--text-secondary);
}
.cell-time {
  white-space: nowrap;
}
.cell-pity {
  font-variant-numeric: tabular-nums;
  font-weight: 500;
}
.badge {
  display: inline-block;
  border-radius: 20px;
  padding: 3px 8px;
  font-size: 10px;
  font-weight: 600;
}
.badge-win {
  color: #326342;
  background: #deeee1;
}
.badge-lose {
  color: #9b4842;
  background: #f6e3df;
}
.badge-guarantee {
  color: #386692;
  background: #e0edf8;
}
.badge-muted {
  color: var(--text-secondary);
}
.table-empty {
  padding: 50px 20px;
  text-align: center;
  color: var(--text-secondary);
}
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 16px 22px;
  font-size: 11px;
  color: var(--text-secondary);
}
.page-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}
.btn-page {
  width: 40px;
  height: 40px;
  background: white;
  color: var(--heading);
  border: 1px solid var(--border-strong);
  border-radius: 8px;
  font-size: 24px;
}
.btn-page:hover:not(:disabled) {
  background: var(--bg-hover);
}
.page-info {
  min-width: 44px;
  text-align: center;
  font-variant-numeric: tabular-nums;
}
.mobile-sort {
  display: none;
}
@media (max-width: 760px) {
  .table-toolbar {
    padding: 18px 16px 12px;
    gap: 16px;
  }
  .history-heading {
    width: 100%;
    justify-content: space-between;
  }
  .history-heading h2 {
    font-size: 22px;
  }
  .table-filters {
    width: 100%;
    gap: 8px;
  }
  .search-field {
    flex: 1;
    min-width: 0;
  }
  .search-field input {
    width: 100%;
  }
  .table-filters select {
    max-width: 125px;
  }
  .mobile-sort {
    display: block;
    padding: 0 16px 14px;
    font-size: 11px;
    color: var(--text-secondary);
  }
  .mobile-sort label {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .mobile-sort select {
    font-size: 12px;
    min-height: 38px;
  }
  .wish-table,
  .wish-table tbody {
    display: block;
    width: 100%;
  }
  .wish-table thead {
    display: none;
  }
  .wish-table tr {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px 12px;
    padding: 16px;
    border-top: 1px solid var(--border);
  }
  .wish-table td {
    border: 0;
    padding: 0;
    min-width: 0;
  }
  .cell-item {
    grid-column: 1 / -1;
  }
  .item-content {
    min-width: 0;
  }
  .item-name {
    overflow-wrap: anywhere;
  }
  .cell-rarity {
    grid-column: 2;
    grid-row: 2;
    text-align: right;
  }
  .cell-pity {
    font-size: 12px;
  }
  .cell-pity::before {
    content: attr(data-label) '  ';
    color: var(--text-secondary);
    font-size: 11px;
    font-weight: 400;
  }
  .cell-pity:nth-child(5) {
    text-align: right;
  }
  .cell-time {
    align-self: center;
    font-size: 10px;
    white-space: normal;
  }
  .cell-result {
    text-align: right;
    font-size: 11px;
  }
  .cell-result::before {
    content: '50/50  ';
    color: var(--text-secondary);
    font-size: 10px;
  }
  .pagination {
    padding: 14px 16px;
  }
  .page-controls {
    gap: 6px;
  }
}
</style>
