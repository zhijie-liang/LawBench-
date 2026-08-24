<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppIcon from '../components/AppIcon.vue'
import { clearAuth, currentUser } from '../services/auth.js'
import { resetWorkspaceStore } from '../composables/useWorkspace.js'

const route = useRoute()
const router = useRouter()
const user = currentUser()
const pageTitle = computed(() => route.meta.title || '工作台')
const navGroups = [
  { label: '工作概览', items: [
    { label: '工作台首页', path: '/workspace/overview', icon: 'overview' },
  ] },
  { label: '智能工作', items: [
    { label: '普通问答', path: '/workspace/basic', icon: 'chat' },
    { label: '流程问答', path: '/workspace/graph', icon: 'workflow' },
    { label: 'Agent 问答', path: '/workspace/agent', icon: 'agent' },
  ] },
  { label: '知识管理', items: [
    { label: '资料入库', path: '/workspace/upload', icon: 'upload' },
    { label: '运行记录', path: '/workspace/records', icon: 'history' },
  ] },
  { label: '企业扩展', items: [
    { label: '能力中心', path: '/workspace/capabilities', icon: 'overview' },
  ] },
]

function logout() {
  clearAuth()
  resetWorkspaceStore()
  router.replace('/login')
}
</script>

<template>
  <main class="enterprise-shell">
    <aside class="enterprise-sidebar">
      <div class="side-brand"><span class="brand-seal">律</span><div><strong>律鉴</strong><small>LAWBENCH · V2</small></div></div>
      <div class="brand-rule"></div>
      <nav aria-label="工作台导航">
        <section v-for="group in navGroups" :key="group.label"><p>{{ group.label }}</p><router-link v-for="item in group.items" :key="item.path" :to="item.path"><AppIcon :name="item.icon"/><span>{{ item.label }}</span><i></i></router-link></section>
      </nav>
      <div class="sidebar-profile"><span class="profile-avatar">{{ user.slice(0, 1).toUpperCase() }}</span><div><strong>{{ user }}</strong><small>已安全登录</small></div><button type="button" title="退出登录" @click="logout"><AppIcon name="logout" :size="17"/></button></div>
    </aside>
    <section class="enterprise-main">
      <header class="enterprise-topbar"><div><span>法律知识工作台</span><b>/</b><strong>{{ pageTitle }}</strong></div><div class="environment-status"><i></i><span>本地安全工作区</span><AppIcon name="shield" :size="16"/></div></header>
      <div class="enterprise-content"><router-view /></div>
      <footer class="enterprise-footer"><span>LawBench v2 · 法律智能问答工作台</span><span>回答内容仅供参考，不构成正式法律意见</span></footer>
    </section>
  </main>
</template>
