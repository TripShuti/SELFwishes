<template>
  <div v-if="stats" class="stats-grid">
    <div class="card stat-card">
      <div class="stat-header">Total wishes</div>
      <div class="stat-big">{{ stats.total_pulls }}</div>
    </div>
    <div class="card stat-card">
      <div class="stat-header">Avg 5★ Pity</div>
      <div class="stat-big">
        {{ stats.avg_pity_5?.toFixed(1) || '-' }}
      </div>
      <div class="stat-sub" v-if="stats.luckiness_5">
        {{ luckLabel(stats.luckiness_5, 'lucky') }}
      </div>
    </div>
    <div class="card stat-card">
      <div class="stat-header">Avg 4★ Pity</div>
      <div class="stat-big">
        {{ stats.avg_pity_4?.toFixed(1) || '-' }}
      </div>
      <div class="stat-sub" v-if="stats.luckiness_4">
        {{ luckLabel(stats.luckiness_4, 'lucky') }}
      </div>
    </div>
    <div class="card stat-card" v-if="stats.known_5050">
      <div class="stat-header">50/50 Record</div>
      <div class="stat-big">
        {{ stats.wins_5050 }}W / {{ stats.losses_5050 }}L
      </div>
      <div class="stat-sub">{{ winRate }}% win rate</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  stats: { type: Object, default: null }
})

const winRate = computed(() => {
  if (!props.stats?.total_5050) return 0
  return ((props.stats.wins_5050 / props.stats.total_5050) * 100).toFixed(1)
})

function luckLabel(val, highLabel) {
  if (val <= 0.5) return 'Very ' + highLabel
  if (val <= 0.8) return highLabel.charAt(0).toUpperCase() + highLabel.slice(1)
  if (val <= 1.0) return 'Average'
  return 'Unlucky'
}
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}
.stat-card {
  position: relative;
  padding: 20px 24px;
}
.stat-header {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 7px;
}
.stat-big {
  font-size: 32px;
  line-height: 1.3;
  font-weight: 650;
  color: var(--heading);
  letter-spacing: -0.8px;
  font-variant-numeric: tabular-nums;
}
.stat-sub {
  font-size: 11px;
  color: var(--green);
  margin-top: 6px;
}
@media (max-width: 760px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    margin-bottom: 20px;
  }
  .stat-card {
    padding: 16px;
  }
  .stat-big {
    font-size: clamp(22px, 6.5vw, 27px);
  }
}
</style>
