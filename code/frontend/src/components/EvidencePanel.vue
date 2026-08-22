<script setup>
import AppIcon from './AppIcon.vue'
defineProps({ evidence: { type: Object, required: true } })
</script>

<template>
  <aside class="evidence-card">
    <header><div><span class="section-kicker">EVIDENCE</span><h2>回答依据</h2></div><span class="stage-chip">{{ evidence.stage || '等待运行' }}</span></header>
    <section><h3><AppIcon name="file" :size="15"/>检索片段 <b>{{ evidence.contexts.length }}</b></h3><div v-if="evidence.contexts.length" class="evidence-list"><article v-for="(context, index) in evidence.contexts" :key="index"><span>{{ String(index + 1).padStart(2, '0') }}</span><p>{{ context }}</p></article></div><div v-else class="panel-empty">提交问题后，这里将展示知识库中的相关资料。</div></section>
    <section><h3><AppIcon name="workflow" :size="15"/>处理轨迹 <b>{{ evidence.trace.length }}</b></h3><ol v-if="evidence.trace.length" class="trace-timeline"><li v-for="(step, index) in evidence.trace" :key="index"><i><AppIcon name="check" :size="11"/></i><span>{{ step }}</span></li></ol><div v-else class="panel-empty">流程节点将在接口返回后显示。</div></section>
  </aside>
</template>
