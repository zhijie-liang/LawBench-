export function createModeState() {
  return {
    messages: [{ role: 'assistant', answer: '你好，我是律鉴法律问答助手。请先上传 TXT 资料，再向我提问，我会基于知识库内容回答。' }],
    evidence: { answer: '', contexts: [], trace: [], stage: '' },
    lastResponse: null,
    lastLabel: '',
  }
}
