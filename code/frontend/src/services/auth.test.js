import { beforeEach, describe, expect, it } from 'vitest'
import { clearAuth, isAuthenticated, setAuthenticated } from './auth.js'

describe('前端认证状态', () => {
  beforeEach(() => sessionStorage.clear())

  it('登录后允许访问工作台', () => {
    setAuthenticated('alice')
    expect(isAuthenticated()).toBe(true)
  })

  it('退出后拒绝访问工作台', () => {
    setAuthenticated('alice')
    clearAuth()
    expect(isAuthenticated()).toBe(false)
  })
})
