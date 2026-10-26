<template>
  <div class="card pity-card">
    <div class="card-header">
      <h4 class="banner-name">
        <span class="banner-icon" aria-hidden="true">{{
          banner.gacha_type === '302' ? '⚔' : '✦'
        }}</span>
        {{ shortName(banner.name) }}
      </h4>
      <span class="pulls-count">{{ banner.total_pulls }} pulls</span>
    </div>

    <div class="pity-section">
      <div class="pity-label">
        <span>5★ Pity</span>
        <span class="pity-value" :class="pityClass5">
          {{ banner.pity_5 }} <small>/ {{ max5 }}</small>
        </span>
      </div>
      <div class="pity-bar">
        <div
          class="pity-fill"
          :class="pityBarClass5"
          :style="{ width: pityPercent5 + '%' }"
        ></div>
      </div>
      <div class="pity-sub">
        {{ Math.max(0, max5 - banner.pity_5) }} wishes to hard pity
      </div>
    </div>

    <div class="pity-section">
      <div class="pity-label">
        <span>4★ Pity</span>
        <span class="pity-value" :class="pityClass4">
          {{ banner.pity_4 }} <small>/ {{ max4 }}</small>
        </span>
      </div>
      <div class="pity-bar">
        <div
          class="pity-fill pity-fill-4"
          :style="{ width: pityPercent4 + '%' }"
        ></div>
      </div>
    </div>

    <div class="stats-row">
      <div class="stat">
        <span class="stat-label">5★ obtained</span>
        <span class="stat-value gold">{{ banner.count_5 }}</span>
      </div>
      <div class="stat">
        <span class="stat-label">4★ obtained</span>
        <span class="stat-value purple">{{ banner.count_4 }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  banner: { type: Object, required: true }
})

const maxPity = {
  301: { 5: 90, 4: 10 },
  302: { 5: 80, 4: 10 },
  200: { 5: 90, 4: 10 },
  100: { 5: 90, 4: 10 },
  500: { 5: 90, 4: 10 }
}

const nameMap = {
  'Character Event Wish': 'Character',
  'Weapon Event Wish': 'Weapon',
  'Standard Wish': 'Standard',
  "Beginners' Wish": 'Beginners',
  'Chronicled Wish': 'Chronicled'
}

const max5 = computed(() => (maxPity[props.banner.gacha_type] || {})[5] || 90)
const max4 = computed(() => (maxPity[props.banner.gacha_type] || {})[4] || 10)

const pityPercent5 = computed(() =>
  Math.min((props.banner.pity_5 / max5.value) * 100, 100)
)
const pityPercent4 = computed(() =>
  Math.min((props.banner.pity_4 / max4.value) * 100, 100)
)

const pityClass5 = computed(() => {
  const p = props.banner.pity_5
  if (p >= max5.value - 10) return 'danger'
  return ''
})

const pityBarClass5 = computed(() => {
  const p = props.banner.pity_5
  if (p >= max5.value - 10) return 'fill-danger'
  return ''
})

const pityClass4 = computed(() => {
  const p = props.banner.pity_4
  if (p >= 8) return 'danger'
  return ''
})

function shortName(name) {
  return nameMap[name] || name
}
</script>

<style scoped>
.pity-card {
  min-width: 0;
}
.card-header {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  align-items: center;
  margin-bottom: 22px;
}
.banner-name {
  font-size: 15px;
  color: var(--heading);
}
.banner-icon {
  color: var(--accent);
  margin-right: 6px;
  font-size: 22px;
  vertical-align: middle;
}
.pulls-count {
  font-size: 11px;
  color: var(--text-secondary);
  white-space: nowrap;
}
.pity-section {
  margin-bottom: 16px;
}
.pity-label {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 12px;
  margin-bottom: 7px;
}
.pity-value {
  color: var(--gold);
  font-weight: 700;
  font-size: 19px;
  font-variant-numeric: tabular-nums;
}
.pity-value small {
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 400;
}
.pity-section:nth-child(3) .pity-value {
  color: var(--purple);
}
.pity-value.danger {
  color: var(--red);
}
.pity-bar {
  height: 6px;
  background: #eee9df;
  border-radius: 6px;
  overflow: hidden;
}
.pity-fill {
  height: 100%;
  background: #cca653;
  border-radius: inherit;
  transition: width 0.3s;
}
.pity-fill.fill-danger {
  background: var(--red);
}
.pity-fill-4 {
  background: #af8bd7;
}
.pity-sub {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 7px;
}
.stats-row {
  display: flex;
  gap: 28px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}
.stat {
  display: flex;
  flex-direction: column-reverse;
  gap: 2px;
}
.stat-label {
  font-size: 10px;
  color: var(--text-secondary);
}
.stat-value {
  font-size: 16px;
  font-weight: 600;
}
.gold {
  color: var(--gold);
}
.purple {
  color: var(--purple);
}
@media (min-width: 361px) and (max-width: 760px) {
  .pity-card {
    padding: 14px;
  }
  .card-header {
    flex-wrap: wrap;
    gap: 0;
    margin-bottom: 14px;
  }
  .pulls-count {
    padding-left: 28px;
  }
  .stats-row {
    gap: 20px;
  }
}
</style>
