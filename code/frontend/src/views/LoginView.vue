<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login, register } from '../services/api.js'
import { setAuthenticated } from '../services/auth.js'
import { validateAuthForm } from '../services/auth-validation.js'
const router = useRouter(), isRegister = ref(false), username = ref(''), password = ref(''), confirmPassword = ref(''), showPassword = ref(false), loading = ref(false), error = ref(''), notice = ref('')
async function submit() {
  error.value = ''; notice.value = ''
  const validationError = validateAuthForm({ username: username.value, password: password.value, confirmPassword: confirmPassword.value, isRegister: isRegister.value })
  if (validationError) return (error.value = validationError)
  loading.value = true
  try {
    const result = isRegister.value ? await register(username.value.trim(), password.value) : await login(username.value.trim(), password.value)
    if (result?.message === '注册成功' || (result?.username && result?.password)) { isRegister.value = false; notice.value = '账号创建成功，请登录'; password.value = ''; confirmPassword.value = '' }
    else if (result?.message === '登录成功') { setAuthenticated(username.value.trim()); await router.push('/workspace') }
    else error.value = typeof result === 'string' ? result : result?.message || '操作未完成'
  } catch (err) { error.value = err.message } finally { loading.value = false }
}
function toggleMode() { isRegister.value = !isRegister.value; error.value = ''; notice.value = ''; password.value = ''; confirmPassword.value = ''; showPassword.value = false }
</script>
<template>
  <main class="auth-page"><section class="auth-visual"><div class="auth-brand"><span class="logo-mark">律</span><div><strong>律鉴</strong><small>LAWBENCH V2</small></div></div><div class="auth-copy"><p class="eyebrow light">LEGAL KNOWLEDGE WORKSPACE</p><h1>让法律资料，<br /><span>真正服务于判断。</span></h1><p>上传资料、智能检索、流程可追踪。<br />把复杂的法律知识，变成清晰的工作依据。</p></div><div class="auth-foot">LawBench v2 · 法律智能问答工作台</div></section><section class="auth-form-area"><div class="auth-card"><div class="mobile-brand"><span class="logo-mark">律</span><strong>律鉴</strong></div><p class="eyebrow">{{ isRegister ? 'CREATE ACCOUNT' : 'WELCOME BACK' }}</p><h2>{{ isRegister ? '创建工作账号' : '欢迎回到律鉴' }}</h2><p class="auth-subtitle">{{ isRegister ? '设置账号信息，注册成功后返回登录。' : '登录后继续你的法律资料工作。' }}</p><form @submit.prevent="submit"><label>用户名<input v-model="username" autocomplete="username" placeholder="请输入用户名" /></label><label>密码<div class="password-field"><input v-model="password" :type="showPassword ? 'text' : 'password'" :autocomplete="isRegister ? 'new-password' : 'current-password'" :placeholder="isRegister ? '至少输入 6 位密码' : '请输入密码'" /><button type="button" @click="showPassword = !showPassword">{{ showPassword ? '隐藏' : '显示' }}</button></div></label><label v-if="isRegister">确认密码<input v-model="confirmPassword" :type="showPassword ? 'text' : 'password'" autocomplete="new-password" placeholder="请再次输入密码" /></label><p v-if="isRegister" class="password-hint">密码至少 6 位，两次输入需保持一致</p><div v-if="error" class="form-alert error">{{ error }}</div><div v-if="notice" class="form-alert success">{{ notice }}</div><button class="primary-button auth-submit" :disabled="loading">{{ loading ? '请稍候…' : (isRegister ? '创建账号' : '进入工作台') }}<span>→</span></button></form><div class="auth-switch">{{ isRegister ? '已经有账号？' : '还没有账号？' }}<button type="button" @click="toggleMode">{{ isRegister ? '返回登录' : '立即注册' }}</button></div><p class="disclaimer">法律分析内容仅供参考，不构成正式法律意见。</p></div></section></main>
</template>
