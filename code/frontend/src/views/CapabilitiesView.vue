<script setup>
import AppIcon from '../components/AppIcon.vue'
import { enterpriseCapabilities } from '../config/capabilities.js'
</script>

<template>
  <div class="page-stack capabilities-page">
    <header class="page-hero"><div><span class="section-kicker">ENTERPRISE CAPABILITY CENTER</span><h1>企业能力中心</h1><p>展示 LawBench 从法律问答工作台向企业级法律知识平台演进的产品蓝图。</p></div><span class="planning-badge">6 项能力规划中</span></header>
    <section class="capability-summary"><div><strong>当前已具备</strong><span>身份访问、资料入库、双模式问答、运行记录</span></div><i></i><div><strong>后续扩展原则</strong><span>接口就绪一项，前端开放一项</span></div><i></i><div><strong>展示口径</strong><span>规划功能不调用虚构数据</span></div></section>
    <section class="capability-full-grid"><article v-for="item in enterpriseCapabilities" :key="item.id"><header><span><AppIcon :name="item.icon" :size="22"/></span><b>{{ item.phase }}</b></header><h2>{{ item.title }}</h2><p>{{ item.description }}</p><div><small>{{ item.tag }}</small><strong>待接入：{{ item.interface }}</strong></div></article></section>
    <section class="delivery-roadmap"><header><span class="section-kicker">DELIVERY ROADMAP</span><h2>产品建设路径</h2></header><ol><li class="complete"><i>1</i><div><strong>基础工作台</strong><span>登录、入库、问答、记录</span></div><b>当前版本</b></li><li><i>2</i><div><strong>知识与模型管理</strong><span>资料中心、案件库、模型配置</span></div><b>接口待建设</b></li><li><i>3</i><div><strong>企业治理能力</strong><span>团队协作、权限与审计</span></div><b>规划阶段</b></li><li><i>4</i><div><strong>数据价值分析</strong><span>质量评估与运营报告</span></div><b>规划阶段</b></li></ol></section>
  </div>
</template>
