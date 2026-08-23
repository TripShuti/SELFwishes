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
  gap: 6px;
  margin-bottom: 24px;
  padding: 5px;
  overflow-x: auto;
  background: rgba(43, 58, 87, 0.75);
  border: 1px solid var(--accent);
  border-radius: var(--radius-lg);
  box-shadow: 0 2px 10px rgba(40, 55, 85, 0.3);
}

.tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid transparent;
  background: transparent;
  color: #c4cddc;
  font-size: 14px;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  border-radius: 7px;
  white-space: nowrap;
  transition: all 0.2s;
}

.tab:hover {
  color: #e8d5a8;
  background: rgba(232, 213, 168, 0.1);
}

.tab.active {
  background: linear-gradient(180deg, #e6c88a 0%, #c9a25c 100%);
  color: #3a2f1c;
  border-color: #a8854a;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.5);
}

.tab-count {
  font-size: 12px;
  opacity: 0.75;
}
</style>
