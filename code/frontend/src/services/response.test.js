import { describe, expect, it } from 'vitest'
import { normalizeChatResponse, safeErrorMessage, stringifyResponse } from './response.js'

describe('问答响应展示', () => {
  it('兼容纯文本普通问答', () => {
    expect(normalizeChatResponse('知识库中没有相关信息')).toMatchObject({ answer: '知识库中没有相关信息', contexts: [], trace: [] })
  })

  it('展示 LangGraph 的回答、上下文和轨迹', () => {
    expect(normalizeChatResponse({ answer: '答案', contexts: ['依据'], trace: ['retrieve'], stage: 'generate' })).toEqual({ answer: '答案', contexts: ['依据'], trace: ['retrieve'], stage: 'generate' })
  })

  it('将对象和数组形式的检索信息转换为可读文本', () => {
    expect(normalizeChatResponse({
      answer: '答案',
      contexts: [{ page_content: '民法典相关条文', source: 'civil.txt' }, 12, null],
      trace: [{ node: 'retrieve' }, { stage: 'answer' }],
    })).toMatchObject({
      contexts: ['民法典相关条文', '12'],
      trace: ['retrieve', 'answer'],
    })
  })

  it('顶层数组响应也能作为回答展示', () => {
    expect(normalizeChatResponse(['第一项', { text: '第二项' }])).toMatchObject({ answer: '第一项 · 第二项', stage: 'answer' })
  })

  it('技术详情隐藏敏感字段和内部堆栈', () => {
    expect(stringifyResponse({ answer: '完成', token: 'secret-value' })).toContain('"token": "***"')
    expect(safeErrorMessage('Traceback (most recent call last):\nValueError: failed')).toBe('服务暂时无法完成请求，请稍后重试')
  })

  it('空响应也可读', () => {
    expect(stringifyResponse(null)).toBe('接口没有返回内容')
  })
})
