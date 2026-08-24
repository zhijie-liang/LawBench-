import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated } from './services/auth.js'
import LoginView from './views/LoginView.vue'
import WorkspaceShell from './layouts/WorkspaceShell.vue'
import BasicChatView from './views/BasicChatView.vue'
import GraphChatView from './views/GraphChatView.vue'
import AgentChatView from './views/AgentChatView.vue'
import UploadView from './views/UploadView.vue'
import RecordsView from './views/RecordsView.vue'
import OverviewView from './views/OverviewView.vue'
import CapabilitiesView from './views/CapabilitiesView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/workspace/overview' },
    { path: '/login', component: LoginView, meta: { guest: true } },
    {
      path: '/workspace', component: WorkspaceShell, meta: { requiresAuth: true }, children: [
        { path: '', redirect: '/workspace/overview' },
        { path: 'overview', component: OverviewView, meta: { title: '工作台首页' } },
        { path: 'basic', component: BasicChatView, meta: { title: '普通问答' } },
        { path: 'graph', component: GraphChatView, meta: { title: '流程问答' } },
        { path: 'agent', component: AgentChatView, meta: { title: 'Agent 问答' } },
        { path: 'upload', component: UploadView, meta: { title: '资料入库' } },
        { path: 'records', component: RecordsView, meta: { title: '运行记录' } },
        { path: 'capabilities', component: CapabilitiesView, meta: { title: '能力中心' } },
      ],
    },
  ],
})
router.beforeEach((to) => {
  if (to.meta.requiresAuth && !isAuthenticated()) return '/login'
  if (to.meta.guest && isAuthenticated()) return '/workspace'
})
export default router
