export function validateAuthForm({ username = '', password = '', confirmPassword = '', isRegister = false } = {}) {
  if (!username.trim() || !password) return '请输入用户名和密码'
  if (!isRegister) return ''
  if (password.length < 6) return '密码至少需要 6 位'
  if (password !== confirmPassword) return '两次输入的密码不一致'
  return ''
}
