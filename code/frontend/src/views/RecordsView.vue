<script setup>
import { computed, ref } from 'vue'
import AppIcon from '../components/AppIcon.vue'
import ResponseDetails from '../components/ResponseDetails.vue'
import { workspaceState } from '../composables/useWorkspace.js'
import { normalizeChatResponse } from '../services/response.js'
import { filterRecords } from '../services/workspace-ui.js'

const typeFilter = ref('all')
const statusFilter = ref('all')
const visibleRecords = computed(() => filterRecords(workspaceState.records, typeFilter.value, statusFilter.value))
const typeOptions = [{ value: 'all', label: '全部业务' }, { value: 'basic', label: '普通问答' }, { value: 'graph', label: '流程问答' }, { value: 'agent', label: 'Agent 问答' }, { value: 'upload', label: '资料入库' }]

function recordSummary(record) {
  if (record.type === 'upload') return typeof record.response === 'string' ? record.response : record.status === 'success' ? '资料入库接口已成功返回。' : '资料入库未完成。'
  return normalizeChatResponse(record.response).answer || (record.status === 'success' ? '接口已返回，但没有回答内容。' : String(record.response || '请求失败'))
}
</script>

<template>
  <div class="page-stack records-page">
    <header class="page-hero"><div><span class="section-kicker">SESSION ACTIVITY</span><h1>运行记录</h1><p>集中查看当前浏览器会话中的资料入库与问答结果。</p></div><span class="record-count">共 {{ workspaceState.records.length }} 条</span></header>
    <section class="records-toolbar"><div class="filter-tabs"><button v-for="option in typeOptions" :key="option.value" type="button" :class="{ active: typeFilter === option.value }" @click="typeFilter = option.value">{{ option.label }}</button></div><select v-model="statusFilter" aria-label="按运行状态筛选"><option value="all">全部状态</option><option value="success">仅成功</option><option value="failed">仅失败</option></select></section>
    <section v-if="visibleRecords.length" class="record-list"><article v-for="record in visibleRecords" :key="record.id" class="business-record"><div class="record-icon" :class="record.type"><AppIcon :name="record.type === 'upload' ? 'upload' : record.type === 'graph' ? 'workflow' : record.type === 'agent' ? 'agent' : 'chat'" :size="19"/></div><div class="record-main"><header><div><strong>{{ record.label }}</strong><span>{{ record.time }}</span></div><b :class="record.status">{{ record.status === 'success' ? '运行成功' : '运行失败' }}</b></header><p>{{ recordSummary(record) }}</p><ResponseDetails :value="record.response"/></div></article></section>
    <section v-else class="records-empty"><span><AppIcon name="history" :size="32"/></span><h2>{{ workspaceState.records.length ? '没有符合条件的记录' : '当前会话还没有运行记录' }}</h2><p>{{ workspaceState.records.length ? '请调整业务类型或运行状态筛选。' : '完成一次问答或资料入库后，记录会显示在这里。' }}</p></section>
  </div>
</template>
