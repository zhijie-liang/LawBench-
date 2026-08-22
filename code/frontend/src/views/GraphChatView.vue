<script setup>
import { computed, ref } from 'vue'
import AppIcon from '../components/AppIcon.vue'
import ChatComposer from '../components/ChatComposer.vue'
import ChatThread from '../components/ChatThread.vue'
import EvidencePanel from '../components/EvidencePanel.vue'
import ResponseDetails from '../components/ResponseDetails.vue'
import StatusNotice from '../components/StatusNotice.vue'
import { addRecord, clearMode, workspaceState } from '../composables/useWorkspace.js'
import { graphChat } from '../services/api.js'
import { currentUser } from '../services/auth.js'
import { normalizeChatResponse, safeErrorMessage } from '../services/response.js'

const user = currentUser()
const question = ref('')
const loading = ref(false)
const error = ref('')
const notice = ref('')
const state = computed(() => workspaceState.graph)

async function ask() {
  const asked = question.value.trim()
  if (!asked || loading.value) return
  state.value.messages.push({ role: 'user', answer: asked })
  question.value = ''
  error.value = ''
  notice.value = ''
  loading.value = true
  try {
    const raw = await graphChat(asked)
    const result = normalizeChatResponse(raw)
    state.value.evidence = result
    state.value.lastResponse = raw
    state.value.lastLabel = '流程问答 /rag/chat'
    state.value.messages.push({ role: 'assistant', answer: result.answer || '流程已完成，但未生成可展示的回答。' })
    addRecord({ type: 'graph', label: '流程问答', response: raw, status: 'success' })
    notice.value = result.answer ? '流程问答已完成' : '流程已完成，但回答内容为空'
  } catch (err) {
    const message = safeErrorMessage(err)
    state.value.messages.push({ role: 'assistant', answer: '流程问答未能完成，请查看错误提示。', failed: true })
    addRecord({ type: 'graph', label: '流程问答', response: message, status: 'failed' })
    error.value = message
  } finally { loading.value = false }
}

function clearConversation() {
  clearMode('graph')
  notice.value = '流程问答记录已清空'
}
</script>

<template>
  <div class="page-stack">
    <header class="page-hero"><div><span class="section-kicker">TRACEABLE LEGAL REASONING</span><h1>流程问答</h1><p>检索资料、执行流程并展示回答依据，让每次结果更加透明。</p></div><button class="secondary-action" type="button" @click="clearConversation">清空对话</button></header>
    <StatusNotice v-if="error" type="error" :message="error" @close="error = ''"/><StatusNotice v-if="notice" :message="notice" @close="notice = ''"/>
    <section class="mode-banner graph"><span><AppIcon name="workflow" :size="21"/></span><div><strong>可追踪检索流程</strong><p>展示 stage、trace 与 contexts，调用 <code>/rag/chat</code></p></div><b>增强模式</b></section>
    <div class="graph-workspace"><section class="graph-chat-card"><ChatThread :messages="state.messages" :user="user" :loading="loading"/><ChatComposer v-model="question" :loading="loading" placeholder="输入需要检索和分析的法律问题…" @submit="ask"/><ResponseDetails v-if="state.lastResponse !== null" :value="state.lastResponse" label="查看本次接口返回"/></section><EvidencePanel :evidence="state.evidence"/></div>
  </div>
</template>
