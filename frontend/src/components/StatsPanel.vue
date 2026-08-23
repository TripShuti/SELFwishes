<template>
  <div v-if="stats" class="stats-grid">
    <div class="card stat-card">
      <div class="stat-header">Total Pulls</div>
      <div class="stat-big">{{ stats.total_pulls }}</div>
    </div>
    <div class="card stat-card">
      <div class="stat-header">Avg 5★ Pity</div>
      <div class="stat-big gold">
        {{ stats.avg_pity_5?.toFixed(1) || '-' }}
      </div>
      <div class="stat-sub" v-if="stats.luckiness_5">
        {{ luckLabel(stats.luckiness_5, 'lucky') }}
      </div>
    </div>
    <div class="card stat-card">
      <div class="stat-header">Avg 4★ Pity</div>
      <div class="stat-big purple">
        {{ stats.avg_pity_4?.toFixed(1) || '-' }}
      </div>
      <div class="stat-sub" v-if="stats.luckiness_4">
        {{ luckLabel(stats.luckiness_4, 'lucky') }}
      </div>
    </div>
    <div class="card stat-card" v-if="stats.known_5050">
      <div class="stat-header">50/50 Record</div>
      <div class="stat-big">{{ stats.wins_5050 }}W / {{ stats.losses_5050 }}L</div>
      <div class="stat-sub">
        {{ winRate }}% win rate
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  stats: { type: Object, default: null },
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
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
}

.stat-header {
  font-size: 13px;
  color: var(--text-secondary);
  letter-spacing: 0.3px;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
  font-style: italic;
}

.stat-big {
  font-size: 30px;
  font-weight: 700;
  color: var(--heading);
}

.stat-big.gold {
  color: var(--gold);
}

.stat-big.purple {
  color: #8a6a2f;
}

.stat-sub {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 4px;
  font-style: italic;
}
</style>
