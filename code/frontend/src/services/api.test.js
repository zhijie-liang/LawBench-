import { afterEach, describe, expect, it, vi } from 'vitest'
import { agentChat, chat, graphChat, login, ragUpload, register } from './api.js'

describe('新版后端接口适配', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('按约定调用注册和登录接口', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(new Response(JSON.stringify({ message: '登录成功' }), { status: 200 })))
    vi.stubGlobal('fetch', fetchMock)
    await register('alice', 'secret')
    await login('alice', 'secret')
    expect(fetchMock.mock.calls[0][0]).toContain('/api/register?username=alice&password=secret')
    expect(fetchMock.mock.calls[1][0]).toContain('/api/login?username=alice&password=secret')
  })

  it('以 multipart 调用上传并以 query 调用两个问答接口', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(new Response(JSON.stringify({ answer: 'ok' }), { status: 200 })))
    vi.stubGlobal('fetch', fetchMock)
    await ragUpload(new File(['合同内容'], 'contract.txt', { type: 'text/plain' }))
    await chat('违约责任是什么')
    await graphChat('违约责任是什么')
    await agentChat('违约责任是什么')
    expect(fetchMock.mock.calls[0][0]).toBe('/api/rag')
    expect(fetchMock.mock.calls[0][1].body).toBeInstanceOf(FormData)
    expect(fetchMock.mock.calls[1][0]).toContain('/api/chat?question=')
    expect(fetchMock.mock.calls[2][0]).toContain('/api/rag/chat?question=')
    expect(fetchMock.mock.calls[3][0]).toContain('/api/agent?question=')
  })
})
