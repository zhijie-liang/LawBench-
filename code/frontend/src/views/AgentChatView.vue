<script setup>
import { computed, ref } from 'vue'
import AppIcon from '../components/AppIcon.vue'
import ChatComposer from '../components/ChatComposer.vue'
import ChatThread from '../components/ChatThread.vue'
import EvidencePanel from '../components/EvidencePanel.vue'
import ResponseDetails from '../components/ResponseDetails.vue'
import StatusNotice from '../components/StatusNotice.vue'
import { addRecord, clearMode, workspaceState } from '../composables/useWorkspace.js'
import { agentChat } from '../services/api.js'
import { currentUser } from '../services/auth.js'
import { normalizeChatResponse, safeErrorMessage } from '../services/response.js'

const user = currentUser()
const question = ref('')
const loading = ref(false)
const error = ref('')
const notice = ref('')
const state = computed(() => workspaceState.agent)
const stages = [
  { key: 'agent', label: 'Agent 决策', hint: '理解问题并选择处理方式' },
  { key: 'tools', label: '工具检索', hint: '调用知识库检索工具' },
  { key: 'collect_contexts', label: '收集依据', hint: '整理可用法律资料' },
  { key: 'grade', label: '相关性判断', hint: '确认依据是否足够' },
  { key: 'answer', label: '生成回答', hint: '基于依据形成结论' },
]

const currentStage = computed(() => state.value.evidence.stage || '')
const stageIndex = computed(() => {
  const index = stages.findIndex((item) => item.key === currentStage.value)
  return index
})
function stageStatus(index, key) {
  if (state.value.evidence.trace.includes(key)) return 'done'
  if (currentStage.value === key) return 'active'
  if (currentStage.value === 'refuse' && key === 'answer') return 'active'
  return stageIndex.value > index ? 'done' : ''
}

async function ask() {
  const asked = question.value.trim()
  if (!asked || loading.value) return
  state.value.messages.push({ role: 'user', answer: asked })
  question.value = ''
  error.value = ''
  notice.value = ''
  loading.value = true
  try {
    const raw = await agentChat(asked)
    const result = normalizeChatResponse(raw)
    state.value.evidence = result
    state.value.lastResponse = raw
    state.value.lastLabel = 'Agent 问答 /agent'
    state.value.messages.push({ role: 'assistant', answer: result.answer || 'Agent 已完成处理，但未生成可展示的回答。' })
    const failed = Boolean(result.error || result.stage === 'error')
    addRecord({ type: 'agent', label: 'Agent 问答', response: raw, status: failed ? 'failed' : 'success' })
    if (failed) error.value = safeErrorMessage(result.error || 'Agent 服务暂时无法完成请求')
    else notice.value = result.answer ? 'Agent 问答已完成' : 'Agent 已完成处理，但回答内容为空'
  } catch (err) {
    const message = safeErrorMessage(err)
    state.value.messages.push({ role: 'assistant', answer: 'Agent 问答未能完成，请查看错误提示。', failed: true })
    addRecord({ type: 'agent', label: 'Agent 问答', response: message, status: 'failed' })
    error.value = message
  } finally { loading.value = false }
}

function clearConversation() {
  clearMode('agent')
  notice.value = 'Agent 问答记录已清空'
}
</script>

<template>
  <div class="page-stack">
    <header class="page-hero"><div><span class="section-kicker">AUTONOMOUS LEGAL AGENT</span><h1>Agent 问答</h1><p>由智能代理自主选择检索工具，并把决策、依据与结果完整呈现。</p></div><button class="secondary-action" type="button" @click="clearConversation">清空对话</button></header>
    <StatusNotice v-if="error" type="error" :message="error" @close="error = ''"/><StatusNotice v-if="notice" :message="notice" @close="notice = ''"/>
    <section class="mode-banner agent"><span><AppIcon name="agent" :size="21"/></span><div><strong>自主代理问答</strong><p>展示 stage、trace、contexts 与安全错误信息，调用 <code>/agent</code></p></div><b>实验能力</b></section>
    <section class="agent-stage-card"><div class="agent-stage-heading"><div><span class="section-kicker">AGENT PIPELINE</span><h2>本次处理轨迹</h2></div><span v-if="currentStage" class="stage-badge">当前：{{ currentStage }}</span></div><div class="agent-stage-list"><div v-for="(item, index) in stages" :key="item.key" class="agent-stage-item" :class="stageStatus(index, item.key)"><span class="agent-stage-number"><AppIcon v-if="stageStatus(index, item.key) === 'done'" name="check" :size="13"/><b v-else>{{ index + 1 }}</b></span><div><strong>{{ item.label }}</strong><small>{{ item.hint }}</small></div></div></div></section>
    <div class="graph-workspace"><section class="graph-chat-card"><ChatThread :messages="state.messages" :user="user" :loading="loading"/><ChatComposer v-model="question" :loading="loading" placeholder="输入需要 Agent 自主检索和分析的法律问题…" @submit="ask"/><ResponseDetails v-if="state.lastResponse !== null" :value="state.lastResponse" label="查看本次接口返回"/></section><EvidencePanel :evidence="state.evidence"/></div>
  </div>
</template>
