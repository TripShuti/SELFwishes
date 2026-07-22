<template>
  <div class="banner-tabs">
    <button
      :class="['tab', { active: activeTab === 'all' }]"
      @click="$emit('update:activeTab', 'all')"
    >
      All
    </button>
    <button
      v-for="b in banners"
      :key="b.gacha_type"
      :class="['tab', { active: activeTab === b.gacha_type }]"
      @click="$emit('update:activeTab', b.gacha_type)"
    >
      <span class="tab-name">{{ shortName(b.name) }}</span>
      <span class="tab-count">{{ b.total_pulls }}</span>
    </button>
  </div>
</template>

<script setup>
defineProps({
  banners: { type: Array, default: () => [] },
  activeTab: { type: String, default: 'all' },
})

defineEmits(['update:activeTab'])

const nameMap = {
  'Character Event Wish': 'Character',
  'Weapon Event Wish': 'Weapon',
  'Standard Wish': 'Standard',
  "Beginners' Wish": 'Beginners',
  'Chronicled Wish': 'Chronicled',
}

function shortName(name) {
  return nameMap[name] || name
}
</script>

<style scoped>
.banner-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 24px;
  background: var(--bg-secondary);
  border-radius: var(--radius);
  padding: 4px;
  overflow-x: auto;
}

.tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border-radius: 6px;
  white-space: nowrap;
  transition: all 0.2s;
}

.tab:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.tab.active {
  background: var(--accent);
  color: white;
}

.tab-count {
  font-size: 11px;
  opacity: 0.7;
}

.tab.active .tab-count {
  opacity: 0.9;
}
</style>
