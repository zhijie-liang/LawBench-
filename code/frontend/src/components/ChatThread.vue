<script setup>
import AppIcon from './AppIcon.vue'
defineProps({ messages: { type: Array, required: true }, user: { type: String, default: '' }, loading: Boolean })
</script>

<template>
  <div class="chat-thread" aria-live="polite">
    <article v-for="(item, index) in messages" :key="index" class="chat-message" :class="item.role">
      <div class="message-avatar">{{ item.role === 'user' ? user.slice(0, 1).toUpperCase() : '律' }}</div>
      <div class="message-content">
        <span>{{ item.role === 'user' ? '我的问题' : '律鉴助手' }}</span>
        <p :class="{ failed: item.failed }">{{ item.answer }}</p>
      </div>
    </article>
    <div v-if="loading" class="thinking-state"><AppIcon name="clock" :size="16"/><span></span><span></span><span></span>正在处理，请稍候</div>
  </div>
</template>
