import { beforeEach, describe, expect, it } from 'vitest'
import router from './router.js'
import { clearAuth, setAuthenticated } from './services/auth.js'

describe('工作台路由保护', () => {
  beforeEach(async () => { clearAuth(); await router.push('/login') })

  it('未登录访问工作台时回到登录页', async () => {
    await router.push('/workspace')
    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('登录后可进入工作台', async () => {
    setAuthenticated('alice')
    await router.push('/workspace')
    expect(router.currentRoute.value.path).toBe('/workspace/overview')
  })

  it('普通问答和流程问答使用独立页面地址', async () => {
    setAuthenticated('alice')
    await router.push('/workspace/basic')
    expect(router.currentRoute.value.path).toBe('/workspace/basic')
    expect(router.currentRoute.value.matched.at(-1).components.default.__name).toBe('BasicChatView')
    await router.push('/workspace/graph')
    expect(router.currentRoute.value.path).toBe('/workspace/graph')
    expect(router.currentRoute.value.matched.at(-1).components.default.__name).toBe('GraphChatView')
  })

  it('Agent 问答拥有独立页面地址', async () => {
    setAuthenticated('alice')
    await router.push('/workspace/agent')
    expect(router.currentRoute.value.matched.at(-1).components.default.__name).toBe('AgentChatView')
  })

  it('企业扩展能力拥有独立展示页面', async () => {
    setAuthenticated('alice')
    await router.push('/workspace/capabilities')
    expect(router.currentRoute.value.matched.at(-1).components.default.__name).toBe('CapabilitiesView')
  })
})
