<script setup>
import AppIcon from './AppIcon.vue'
defineProps({ modelValue: { type: String, default: '' }, loading: Boolean, placeholder: { type: String, default: '请输入法律问题' } })
defineEmits(['update:modelValue', 'submit'])
</script>

<template>
  <form class="chat-composer" @submit.prevent="$emit('submit')">
    <textarea :value="modelValue" rows="3" :placeholder="placeholder" :disabled="loading" @input="$emit('update:modelValue', $event.target.value)" @keydown.enter.exact.prevent="$emit('submit')"></textarea>
    <div class="composer-footer"><span>Enter 发送 · Shift + Enter 换行</span><button type="submit" :disabled="loading || !modelValue.trim()"><span>{{ loading ? '处理中' : '发送问题' }}</span><AppIcon name="send" :size="16"/></button></div>
  </form>
</template>
