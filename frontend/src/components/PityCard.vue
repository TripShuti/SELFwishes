<template>
  <div class="card pity-card">
    <div class="card-header">
      <h4 class="banner-name">{{ shortName(banner.name) }}</h4>
      <span class="pulls-count">{{ banner.total_pulls }} pulls</span>
    </div>

    <div class="pity-section">
      <div class="pity-label">
        <span>5★ Pity</span>
        <span class="pity-value" :class="pityClass5">
          {{ banner.pity_5 }}
        </span>
      </div>
      <div class="pity-bar">
        <div
          class="pity-fill"
          :class="pityBarClass5"
          :style="{ width: pityPercent5 + '%' }"
        ></div>
      </div>
      <div class="pity-sub">Guaranteed at {{ max5 }}</div>
    </div>

    <div class="pity-section">
      <div class="pity-label">
        <span>4★ Pity</span>
        <span class="pity-value" :class="pityClass4">
          {{ banner.pity_4 }}
        </span>
      </div>
      <div class="pity-bar">
        <div
          class="pity-fill pity-fill-4"
          :style="{ width: pityPercent4 + '%' }"
        ></div>
      </div>
      <div class="pity-sub">Guaranteed at {{ max4 }}</div>
    </div>

    <div class="stats-row">
      <div class="stat">
        <span class="stat-label">5★</span>
        <span class="stat-value gold">{{ banner.count_5 }}</span>
      </div>
      <div class="stat">
        <span class="stat-label">4★</span>
        <span class="stat-value purple">{{ banner.count_4 }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  banner: { type: Object, required: true },
})

const maxPity = {
  '301': { 5: 90, 4: 10 },
  '302': { 5: 80, 4: 10 },
  '200': { 5: 90, 4: 10 },
  '100': { 5: 90, 4: 10 },
  '500': { 5: 90, 4: 10 },
}

const nameMap = {
  'Character Event Wish': 'Character',
  'Weapon Event Wish': 'Weapon',
  'Standard Wish': 'Standard',
  "Beginners' Wish": 'Beginners',
  'Chronicled Wish': 'Chronicled',
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
  if (p >= max5.value / 2) return 'warning'
  return ''
})

const pityBarClass5 = computed(() => {
  const p = props.banner.pity_5
  if (p >= max5.value - 10) return 'fill-danger'
  if (p >= max5.value / 2) return 'fill-warning'
  return ''
})

const pityClass4 = computed(() => {
  const p = props.banner.pity_4
  if (p >= 8) return 'danger'
  if (p >= 5) return 'warning'
  return ''
})

function shortName(name) {
  return nameMap[name] || name
}
</script>

<style scoped>
.pity-card {
  min-width: 260px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.banner-name {
  font-size: 15px;
  font-weight: 600;
}

.pulls-count {
  font-size: 12px;
  color: var(--text-secondary);
}

.pity-section {
  margin-bottom: 14px;
}

.pity-label {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  margin-bottom: 6px;
}

.pity-value {
  font-weight: 700;
  font-size: 16px;
}

.pity-value.warning {
  color: var(--gold);
}

.pity-value.danger {
  color: var(--red);
}

.pity-bar {
  height: 8px;
  background: var(--bg-primary);
  border-radius: 4px;
  overflow: hidden;
}

.pity-fill {
  height: 100%;
  background: var(--blue);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.pity-fill.fill-warning {
  background: var(--gold);
}

.pity-fill.fill-danger {
  background: var(--red);
}

.pity-fill-4 {
  background: var(--purple);
}

.pity-sub {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.stats-row {
  display: flex;
  gap: 24px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-label {
  font-size: 11px;
  color: var(--text-secondary);
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
}

.stat-value.gold {
  color: var(--gold);
}

.stat-value.purple {
  color: var(--purple);
}
</style>
