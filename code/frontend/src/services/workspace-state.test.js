import { beforeEach, describe, expect, it } from 'vitest'
import { clearWorkspaceState, createWorkspaceState, loadWorkspaceState, saveWorkspaceState } from './workspace-state.js'

describe('工作区会话状态', () => {
  beforeEach(() => sessionStorage.clear())

  it('刷新页面后恢复三种问答和运行记录', () => {
    const state = createWorkspaceState()
    state.basic.messages.push({ role: 'user', answer: '普通问题' })
    state.graph.evidence.contexts.push('检索依据')
    state.agent.evidence.trace.push('tools')
    state.records.push({ id: 'record-1', type: 'graph', status: 'success' })

    saveWorkspaceState(state)

    expect(loadWorkspaceState()).toMatchObject({
      basic: { messages: [{ role: 'assistant' }, { role: 'user', answer: '普通问题' }] },
      graph: { evidence: { contexts: ['检索依据'] } },
      agent: { evidence: { trace: ['tools'] } },
      records: [{ id: 'record-1', type: 'graph', status: 'success' }],
    })
  })

  it('存储内容损坏时安全回退到空工作区', () => {
    sessionStorage.setItem('lawbench-v2-workspace-state', '{broken')
    const state = loadWorkspaceState()

    expect(state.records).toEqual([])
    expect(state.basic.messages).toHaveLength(1)
    expect(state.graph.messages).toHaveLength(1)
    expect(state.agent.messages).toHaveLength(1)
  })

  it('退出登录时可以清除工作区记录', () => {
    saveWorkspaceState(createWorkspaceState())
    clearWorkspaceState()
    expect(sessionStorage.getItem('lawbench-v2-workspace-state')).toBeNull()
  })
})
