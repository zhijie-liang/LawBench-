import { describe, expect, it } from 'vitest'
import { getRecommendedAction, getWorkspaceSummary } from './workspace-summary.js'

describe('工作台概览', () => {
  const records = [
    { type: 'graph', status: 'success', label: '流程问答' },
    { type: 'basic', status: 'failed', label: '普通问答' },
    { type: 'upload', status: 'success', label: '资料入库' },
  ]

  it('只根据当前会话记录计算业务统计', () => {
    expect(getWorkspaceSummary(records)).toEqual({ total: 3, questions: 2, uploads: 1, successRate: 67, serviceStatus: '运行正常' })
  })

  it('按实际使用进度推荐下一步', () => {
    expect(getRecommendedAction([])).toMatchObject({ path: '/workspace/upload' })
    expect(getRecommendedAction([{ type: 'upload', status: 'success' }])).toMatchObject({ path: '/workspace/graph' })
    expect(getRecommendedAction(records)).toMatchObject({ path: '/workspace/records' })
  })
})
