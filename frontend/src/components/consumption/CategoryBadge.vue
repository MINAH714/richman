<!-- src/components/consumption/CategoryBadge.vue -->
<template>
  <span class="badge" :style="{ background: COLOR_MAP[category] || '#eee', color: '#fff' }">
    {{ label }}
  </span>
</template>

<script setup>
defineProps({ category: String, label: String })

const COLOR_MAP = {
  food:         '#FF6B6B',
  cafe:         '#A78BFA',
  transport:    '#34D399',
  shopping:     '#F59E0B',
  convenience:  '#60A5FA',
  health:       '#10B981',
  culture:      '#EC4899',
  telecom:      '#6366F1',
  subscription: '#8B5CF6',
  rent:         '#EF4444',
  transfer:     '#9CA3AF',
  etc:          '#D1D5DB',
}
</script>

<style scoped>
.badge { font-size:.7rem; border-radius:4px; padding:2px 6px; }
</style>