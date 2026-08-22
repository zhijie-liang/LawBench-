import { describe, expect, it } from 'vitest'
import { createModeState } from './mode-state.js'

describe('问答模式状态隔离', () => {
  it('每种模式拥有独立消息和证据状态', () => {
    const basic = createModeState()
    const graph = createModeState()
    basic.messages.push({ role: 'user', answer: '普通问题' })
    basic.evidence.contexts.push('普通依据')

    expect(graph.messages).toHaveLength(1)
    expect(graph.evidence.contexts).toHaveLength(0)
  })
})
