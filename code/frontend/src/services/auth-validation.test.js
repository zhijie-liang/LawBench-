import { describe, expect, it } from 'vitest'
import { validateAuthForm } from './auth-validation.js'

describe('登录注册表单校验', () => {
  it('登录必须填写用户名和密码', () => {
    expect(validateAuthForm({ username: '', password: '', isRegister: false })).toBe('请输入用户名和密码')
  })

  it('注册密码至少六位并需要二次确认', () => {
    expect(validateAuthForm({ username: 'alice', password: '123', confirmPassword: '123', isRegister: true })).toBe('密码至少需要 6 位')
    expect(validateAuthForm({ username: 'alice', password: '123456', confirmPassword: '654321', isRegister: true })).toBe('两次输入的密码不一致')
  })

  it('符合要求时允许提交', () => {
    expect(validateAuthForm({ username: 'alice', password: '123456', confirmPassword: '123456', isRegister: true })).toBe('')
  })
})
