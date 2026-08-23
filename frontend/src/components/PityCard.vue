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
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border);
}

.banner-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--heading);
}

.pulls-count {
  font-size: 13px;
  color: var(--text-secondary);
  font-style: italic;
}

.pity-section {
  margin-bottom: 14px;
}

.pity-label {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 14px;
  margin-bottom: 6px;
  color: var(--heading);
}

.pity-value {
  font-weight: 700;
  font-size: 18px;
  color: var(--heading);
}

.pity-value.warning {
  color: var(--gold);
}

.pity-value.danger {
  color: var(--red);
}

.pity-bar {
  height: 10px;
  background: #e6dcc2;
  border: 1px solid var(--border);
  border-radius: 5px;
  overflow: hidden;
}

.pity-fill {
  height: 100%;
  background: linear-gradient(180deg, #6ea6e0 0%, #4a90d9 100%);
  border-radius: 5px;
  transition: width 0.3s ease;
}

.pity-fill.fill-warning {
  background: linear-gradient(180deg, #e3b45e 0%, #d29a3a 100%);
}

.pity-fill.fill-danger {
  background: linear-gradient(180deg, #d4725e 0%, #c75b4a 100%);
}

.pity-fill-4 {
  background: linear-gradient(180deg, #c9a25c 0%, #a8854a 100%);
}

.pity-sub {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
  font-style: italic;
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
  font-size: 12px;
  color: var(--text-secondary);
}

.stat-value {
  font-size: 19px;
  font-weight: 700;
  color: var(--heading);
}

.stat-value.gold {
  color: var(--gold);
}

.stat-value.purple {
  color: #8a6a2f;
}
</style>
