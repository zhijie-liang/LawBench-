<script setup>
import AppIcon from './AppIcon.vue'
defineProps({ type: { type: String, default: 'success' }, message: { type: String, required: true } })
defineEmits(['close'])
</script>

<template>
  <div class="status-notice" :class="`is-${type}`" role="status">
    <AppIcon :name="type === 'error' ? 'alert' : 'check'" :size="16" />
    <span>{{ message }}</span>
    <button type="button" aria-label="关闭提示" @click="$emit('close')">×</button>
  </div>
</template>
