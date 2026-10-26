<template>
  <div class="banner-tabs">
    <button
      :class="['tab', { active: activeTab === 'all' }]"
      @click="$emit('update:activeTab', 'all')"
    >
      All banners
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
  activeTab: { type: String, default: 'all' }
})

defineEmits(['update:activeTab'])

const nameMap = {
  'Character Event Wish': 'Character',
  'Weapon Event Wish': 'Weapon',
  'Standard Wish': 'Standard',
  "Beginners' Wish": 'Beginners',
  'Chronicled Wish': 'Chronicled'
}

function shortName(name) {
  return nameMap[name] || name
}
</script>

<style scoped>
.banner-tabs {
  display: flex;
  gap: 6px;
  padding: 5px;
  margin-bottom: 20px;
  overflow-x: auto;
  background: #e3ebf1;
  border: 1px solid #d8e2e9;
  border-radius: 10px;
  scrollbar-width: thin;
}
.tab {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 18px;
  min-height: 42px;
  border: 0;
  background: transparent;
  color: #52657c;
  font-size: 13px;
  font-weight: 600;
  border-radius: 7px;
  white-space: nowrap;
}
.tab:hover {
  background: #ffffff70;
}
.tab.active {
  color: var(--heading);
  background: var(--bg-card);
  box-shadow:
    0 1px 4px #1d355515,
    inset 0 -2px var(--accent);
}
.tab-count {
  font-size: 11px;
  font-weight: 400;
}
@media (max-width: 760px) {
  .tab {
    padding: 10px 14px;
  }
}
</style>
