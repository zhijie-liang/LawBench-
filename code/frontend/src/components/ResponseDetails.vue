<script setup>
import { stringifyResponse } from '../services/response.js'
defineProps({ value: { default: null }, label: { type: String, default: '查看技术详情' } })
</script>

<template>
  <details class="response-details">
    <summary>{{ label }}<span>仅展示已脱敏的接口返回</span></summary>
    <pre>{{ stringifyResponse(value) }}</pre>
  </details>
</template>
