import { beforeEach, describe, expect, it } from 'vitest'
import { addRecord, clearMode, resetWorkspaceStore, workspaceState } from './useWorkspace.js'

describe('工作区共享状态', () => {
  beforeEach(() => {
    sessionStorage.clear()
    resetWorkspaceStore()
  })

  it('记录接口结果并生成可筛选的业务记录', () => {
    addRecord({ type: 'graph', label: '流程问答', response: { answer: '结论' }, status: 'success' })

    expect(workspaceState.records[0]).toMatchObject({ type: 'graph', label: '流程问答', status: 'success' })
    expect(workspaceState.records[0].id).toBeTruthy()
  })

  it('只清空指定问答页面', () => {
    workspaceState.basic.messages.push({ role: 'user', answer: '普通问题' })
    workspaceState.graph.messages.push({ role: 'user', answer: '流程问题' })

    clearMode('basic')

    expect(workspaceState.basic.messages).toHaveLength(1)
    expect(workspaceState.graph.messages).toHaveLength(2)
  })
})
