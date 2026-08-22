<script setup>
import { computed, ref } from 'vue'
import AppIcon from '../components/AppIcon.vue'
import ResponseDetails from '../components/ResponseDetails.vue'
import StatusNotice from '../components/StatusNotice.vue'
import { addRecord } from '../composables/useWorkspace.js'
import { ragUpload } from '../services/api.js'
import { safeErrorMessage } from '../services/response.js'
import { getUploadPhase } from '../services/workspace-ui.js'

const file = ref(null)
const loading = ref(false)
const error = ref('')
const notice = ref('')
const result = ref(null)
const phase = computed(() => getUploadPhase({ file: file.value, loading: loading.value, error: error.value, notice: notice.value }))

function chooseFile(event) {
  const selected = event.target.files?.[0] || null
  error.value = ''
  notice.value = ''
  result.value = null
  if (selected && !selected.name.toLowerCase().endsWith('.txt')) {
    file.value = null
    error.value = '当前仅支持 TXT 格式文件'
    event.target.value = ''
    return
  }
  file.value = selected
}

async function upload() {
  if (!file.value || loading.value) return
  loading.value = true
  error.value = ''
  notice.value = ''
  try {
    const raw = await ragUpload(file.value)
    result.value = raw
    addRecord({ type: 'upload', label: `资料入库 · ${file.value.name}`, response: raw, status: 'success' })
    notice.value = typeof raw === 'string' && raw.trim() ? raw : '资料已提交并完成入库'
    file.value = null
  } catch (err) {
    const message = safeErrorMessage(err)
    addRecord({ type: 'upload', label: `资料入库 · ${file.value.name}`, response: message, status: 'failed' })
    error.value = message
  } finally { loading.value = false }
}
</script>

<template>
  <div class="page-stack upload-page">
    <header class="page-hero"><div><span class="section-kicker">KNOWLEDGE INGESTION</span><h1>资料入库</h1><p>将法律文本提交至知识库，为后续检索与问答提供可靠依据。</p></div></header>
    <StatusNotice v-if="error" type="error" :message="error" @close="error = ''"/><StatusNotice v-if="notice" :message="notice" @close="notice = ''"/>
    <ol class="upload-steps"><li :class="{ active: phase === 'select' || phase === 'ready' }"><i>1</i><div><strong>选择资料</strong><span>仅支持 TXT 文件</span></div></li><li :class="{ active: phase === 'processing' }"><i>2</i><div><strong>提交处理</strong><span>以后端真实结果为准</span></div></li><li :class="{ active: phase === 'success' || phase === 'error' }"><i>3</i><div><strong>查看结果</strong><span>确认入库状态</span></div></li></ol>
    <section class="upload-workspace"><div class="upload-card"><div class="upload-card-head"><span><AppIcon name="upload" :size="23"/></span><div><h2>上传法律资料</h2><p>选择 UTF-8 编码的文本文件，确认后开始入库。</p></div></div><label class="file-drop" :class="{ ready: file }"><input type="file" accept=".txt,text/plain" :disabled="loading" @change="chooseFile"/><span class="file-icon"><AppIcon name="file" :size="28"/></span><strong>{{ file ? file.name : '选择或拖入 TXT 文件' }}</strong><small>{{ file ? `${(file.size / 1024).toFixed(1)} KB · 已准备提交` : '文件内容将发送至本地后端进行处理' }}</small></label><div class="upload-actions"><div><AppIcon name="shield" :size="15"/><span>资料仅提交至当前配置的服务</span></div><button class="primary-action" type="button" :disabled="!file || loading" @click="upload">{{ loading ? '正在等待接口返回…' : '确认并开始入库' }}</button></div></div><aside class="upload-guidance"><span class="section-kicker">UPLOAD GUIDE</span><h2>入库说明</h2><ul><li><i><AppIcon name="check" :size="12"/></i><span><strong>文件格式</strong>当前接口仅接收 .txt 文本。</span></li><li><i><AppIcon name="check" :size="12"/></i><span><strong>处理进度</strong>不模拟进度，以接口返回为准。</span></li><li><i><AppIcon name="check" :size="12"/></i><span><strong>结果留存</strong>本次会话可在运行记录中查看。</span></li></ul></aside></section>
    <section v-if="result !== null" class="result-card"><div><span class="result-icon"><AppIcon name="check" :size="20"/></span><div><span class="section-kicker">INGESTION RESULT</span><h2>资料入库完成</h2></div></div><ResponseDetails :value="result" label="查看入库接口返回"/></section>
  </div>
</template>
