import { describe, expect, it } from 'vitest'
import { filterRecords, getUploadPhase } from './workspace-ui.js'

describe('企业工作台交互规则', () => {
  const records = [
    { type: 'basic', status: 'success' },
    { type: 'graph', status: 'failed' },
    { type: 'upload', status: 'success' },
  ]

  it('按业务类型和运行状态筛选记录', () => {
    expect(filterRecords(records, 'graph', 'all')).toEqual([{ type: 'graph', status: 'failed' }])
    expect(filterRecords(records, 'all', 'success')).toHaveLength(2)
    expect(filterRecords(records, 'all', 'all')).toHaveLength(3)
  })

  it('上传区根据真实状态呈现阶段', () => {
    expect(getUploadPhase({ file: null })).toBe('select')
    expect(getUploadPhase({ file: { name: 'law.txt' } })).toBe('ready')
    expect(getUploadPhase({ file: { name: 'law.txt' }, loading: true })).toBe('processing')
    expect(getUploadPhase({ notice: '入库成功' })).toBe('success')
    expect(getUploadPhase({ error: '入库失败' })).toBe('error')
  })
})
