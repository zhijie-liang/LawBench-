<script setup>
import { computed } from 'vue'
import AppIcon from '../components/AppIcon.vue'
import ResponseDetails from '../components/ResponseDetails.vue'
import { workspaceState } from '../composables/useWorkspace.js'
import { currentUser } from '../services/auth.js'
import { getRecommendedAction, getWorkspaceSummary } from '../services/workspace-summary.js'
import { enterpriseCapabilities } from '../config/capabilities.js'

const user = currentUser()
const summary = computed(() => getWorkspaceSummary(workspaceState.records))
const recommendation = computed(() => getRecommendedAction(workspaceState.records))
const recentRecords = computed(() => workspaceState.records.slice(0, 3))
const statCards = computed(() => [
  { label: '本次运行', value: summary.value.total, unit: '次', icon: 'history', tone: 'green' },
  { label: '法律问答', value: summary.value.questions, unit: '次', icon: 'chat', tone: 'gold' },
  { label: '资料入库', value: summary.value.uploads, unit: '次', icon: 'upload', tone: 'blue' },
  { label: '成功率', value: summary.value.successRate, unit: '%', icon: 'check', tone: 'green' },
])
const roadmapItems = enterpriseCapabilities
</script>

<template>
  <div class="page-stack overview-page">
    <header class="overview-hero"><div><span class="section-kicker">GOOD DAY, {{ user.toUpperCase() }}</span><h1>法律知识工作台</h1><p>从资料入库到可追踪问答，在一个工作区完成法律知识处理。</p></div><div class="service-pill" :class="summary.serviceStatus === '运行正常' ? 'online' : ''"><i></i><span>{{ summary.serviceStatus }}</span><small>基于当前会话</small></div></header>
    <section class="stats-grid"><article v-for="card in statCards" :key="card.label" class="stat-card"><span :class="card.tone"><AppIcon :name="card.icon" :size="20"/></span><div><p>{{ card.label }}</p><strong>{{ card.value }}<small>{{ card.unit }}</small></strong></div></article></section>
    <section class="overview-main-grid"><article class="next-action-card"><span class="section-kicker">RECOMMENDED NEXT STEP</span><h2>{{ recommendation.title }}</h2><p>{{ recommendation.description }}</p><router-link :to="recommendation.path">{{ recommendation.action }}<span>→</span></router-link><div class="workflow-path"><div class="done"><i>1</i><span>资料入库</span></div><b></b><div :class="{ done: summary.questions > 0 }"><i>2</i><span>智能问答</span></div><b></b><div :class="{ done: summary.total > 0 }"><i>3</i><span>结果复核</span></div></div></article><article class="capability-card"><span class="section-kicker">CORE CAPABILITIES</span><h2>选择问答方式</h2><router-link to="/workspace/basic"><span><AppIcon name="chat" :size="19"/></span><div><strong>普通问答</strong><p>快速检索并获取简明回答</p></div><b>→</b></router-link><router-link to="/workspace/graph"><span class="gold"><AppIcon name="workflow" :size="19"/></span><div><strong>流程问答</strong><p>展示检索依据与处理轨迹</p></div><b>→</b></router-link></article></section>
    <section class="recent-section"><header><div><span class="section-kicker">RECENT ACTIVITY</span><h2>最近运行</h2></div><router-link v-if="recentRecords.length" to="/workspace/records">查看全部 →</router-link></header><div v-if="recentRecords.length" class="recent-list"><article v-for="record in recentRecords" :key="record.id"><span><AppIcon :name="record.type === 'upload' ? 'upload' : record.type === 'graph' ? 'workflow' : 'chat'" :size="17"/></span><div><strong>{{ record.label }}</strong><small>{{ record.time }}</small></div><b :class="record.status">{{ record.status === 'success' ? '成功' : '失败' }}</b><ResponseDetails :value="record.response" label="详情"/></article></div><div v-else class="overview-empty"><AppIcon name="history" :size="24"/><div><strong>还没有运行记录</strong><p>从资料入库开始，系统会在这里汇总本次会话。</p></div></div></section>
    <section class="roadmap-section"><header><div><span class="section-kicker">ENTERPRISE ROADMAP</span><h2>企业扩展能力</h2><p>以下能力已纳入产品规划，待后续接口接入后逐步开放。</p></div><router-link to="/workspace/capabilities">查看能力中心 →</router-link></header><div class="roadmap-grid"><article v-for="item in roadmapItems" :key="item.title"><div><span><AppIcon :name="item.icon" :size="19"/></span><b>规划中</b></div><h3>{{ item.title }}</h3><p>{{ item.description }}</p><small>{{ item.tag }}</small></article></div></section>
  </div>
</template>
