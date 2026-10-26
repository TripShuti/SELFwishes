<template>
  <span :class="['item-icon', `item-icon--${rarity}`]" aria-hidden="true">
    <img
      v-if="src && !failed"
      :src="src"
      alt=""
      loading="lazy"
      decoding="async"
      @error="failed = true"
    />
    <span v-else class="item-icon-fallback">{{
      itemType === 'Character' ? '✦' : '⚔'
    }}</span>
  </span>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import catalog from '../catalog/item-icons.json'
const props = defineProps({
  itemId: { type: String, default: '' },
  name: String,
  itemType: String,
  rarity: Number
})
const failed = ref(false)
const src = computed(() => {
  const entry =
    catalog.items[props.itemId] ||
    catalog.items[catalog.names[props.name?.toLowerCase()]]
  return entry ? `/icons/items/${entry}.png` : ''
})
watch(src, () => {
  failed.value = false
})
</script>

<style scoped>
.item-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  flex: 0 0 42px;
  overflow: hidden;
  border-radius: 9px;
  background: linear-gradient(145deg, #8bb6ce, #d7e7f0);
}
.item-icon--4 {
  background: linear-gradient(145deg, #a58ac1, #e6dbf2);
}
.item-icon--5 {
  background: linear-gradient(145deg, #c9a069, #f3e2be);
}
.item-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.item-icon-fallback {
  color: #fff;
  font-size: 24px;
  text-shadow: 0 1px 3px #21334b55;
}
</style>
