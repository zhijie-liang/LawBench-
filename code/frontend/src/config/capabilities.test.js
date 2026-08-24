import { describe, expect, it } from 'vitest'
import { enterpriseCapabilities } from './capabilities.js'

describe('企业能力中心规划项', () => {
  it('包含企业与个人知识库分层能力', () => {
    expect(enterpriseCapabilities.map((item) => item.id)).toEqual(expect.arrayContaining(['enterprise-knowledge', 'personal-knowledge']))
  })

  it('包含完整案例智能分析能力', () => {
    const item = enterpriseCapabilities.find((entry) => entry.id === 'case-analysis')
    expect(item).toMatchObject({ phase: '第二阶段', tag: '案例智能分析' })
    expect(item.description).toContain('摘要')
    expect(item.description).toContain('建议方案')
  })
})
