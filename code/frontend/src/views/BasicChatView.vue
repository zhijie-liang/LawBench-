<script setup>
import { computed, ref } from 'vue'
import ChatComposer from '../components/ChatComposer.vue'
import ChatThread from '../components/ChatThread.vue'
import ResponseDetails from '../components/ResponseDetails.vue'
import StatusNotice from '../components/StatusNotice.vue'
import AppIcon from '../components/AppIcon.vue'
import { addRecord, clearMode, workspaceState } from '../composables/useWorkspace.js'
import { chat } from '../services/api.js'
import { currentUser } from '../services/auth.js'
import { normalizeChatResponse, safeErrorMessage } from '../services/response.js'

const user = currentUser()
const question = ref('')
const loading = ref(false)
const error = ref('')
const notice = ref('')
const state = computed(() => workspaceState.basic)
const suggestions = ['合同违约责任如何承担？', '劳动合同解除需要哪些条件？', '民间借贷利息如何认定？']

async function ask() {
  const asked = question.value.trim()
  if (!asked || loading.value) return
  state.value.messages.push({ role: 'user', answer: asked })
  question.value = ''
  error.value = ''
  notice.value = ''
  loading.value = true
  try {
    const raw = await chat(asked)
    const result = normalizeChatResponse(raw)
    state.value.evidence = result
    state.value.lastResponse = raw
    state.value.lastLabel = '普通问答 /chat'
    state.value.messages.push({ role: 'assistant', answer: result.answer || '知识库没有返回可展示的回答。' })
    addRecord({ type: 'basic', label: '普通问答', response: raw, status: 'success' })
    notice.value = result.answer ? '回答已生成' : '接口已完成，但没有返回回答内容'
  } catch (err) {
    const message = safeErrorMessage(err)
    state.value.messages.push({ role: 'assistant', answer: '本次问答未能完成，请稍后重试。', failed: true })
    addRecord({ type: 'basic', label: '普通问答', response: message, status: 'failed' })
    error.value = message
  } finally { loading.value = false }
}

function clearConversation() {
  clearMode('basic')
  notice.value = '普通问答记录已清空'
}
</script>

<template>
  <div class="page-stack basic-chat-page">
    <header class="page-hero"><div><span class="section-kicker">QUICK LEGAL ANSWER</span><h1>普通问答</h1><p>基于已入库资料，快速获取简明、可读的法律问题回答。</p></div><button class="secondary-action" type="button" @click="clearConversation">清空对话</button></header>
    <StatusNotice v-if="error" type="error" :message="error" @close="error = ''"/><StatusNotice v-if="notice" :message="notice" @close="notice = ''"/>
    <section class="mode-banner basic"><span><AppIcon name="chat" :size="21"/></span><div><strong>知识库直接问答</strong><p>适合快速咨询与明确问题，调用 <code>/chat</code></p></div><b>快速模式</b></section>
    <section class="basic-chat-card"><ChatThread :messages="state.messages" :user="user" :loading="loading"/><div class="suggestion-row"><span>常用问题</span><button v-for="item in suggestions" :key="item" type="button" @click="question = item">{{ item }}</button></div><ChatComposer v-model="question" :loading="loading" placeholder="请输入需要咨询的法律问题…" @submit="ask"/></section>
    <ResponseDetails v-if="state.lastResponse !== null" :value="state.lastResponse" label="查看本次接口返回"/>
  </div>
</template>
