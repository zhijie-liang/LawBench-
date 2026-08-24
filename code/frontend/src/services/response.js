const SENSITIVE_KEY = /password|passwd|token|secret|api[_-]?key|authorization|cookie/i
const TRACEBACK = /traceback|file\s+".*",\s+line\s+\d+|\b(?:value|type|runtime|key)error\b/i

function toDisplayText(value, preferredKeys = []) {
  if (value == null || value === '') return ''
  if (typeof value === 'string') return value
  if (typeof value === 'number' || typeof value === 'boolean') return String(value)
  if (Array.isArray(value)) return value.map((item) => toDisplayText(item, preferredKeys)).filter(Boolean).join(' · ')
  for (const key of preferredKeys) {
    const text = toDisplayText(value?.[key], preferredKeys)
    if (text) return text
  }
  try { return JSON.stringify(value) } catch { return '无法解析的返回内容' }
}

export function normalizeChatResponse(data) {
  if (typeof data === 'string') return { answer: data, contexts: [], trace: [], stage: 'answer' }
  if (Array.isArray(data)) return { answer: toDisplayText(data, ['answer', 'message', 'text', 'content', 'page_content']), contexts: [], trace: [], stage: 'answer' }
  return {
    answer: toDisplayText(data?.answer ?? data?.message, ['answer', 'message', 'content', 'text']),
    contexts: (Array.isArray(data?.contexts) ? data.contexts : []).map((item) => toDisplayText(item, ['page_content', 'text', 'content', 'document'])).filter(Boolean),
    trace: (Array.isArray(data?.trace) ? data.trace : []).map((item) => toDisplayText(item, ['node', 'stage', 'name', 'message'])).filter(Boolean),
    stage: toDisplayText(data?.stage, ['stage', 'name']),
    ...(data?.error ? { error: toDisplayText(data.error, ['message', 'detail', 'error']) } : {}),
  }
}

export function safeErrorMessage(error) {
  const message = typeof error === 'string' ? error : error?.message || '请求失败，请稍后重试'
  if (TRACEBACK.test(message)) return '服务暂时无法完成请求，请稍后重试'
  const firstLine = message.split(/\r?\n/)[0].replace(/(password|token|secret|api[_-]?key)\s*[:=]\s*\S+/ig, '$1=***')
  return firstLine.slice(0, 180) || '请求失败，请稍后重试'
}

export function stringifyResponse(data) {
  if (data == null || data === '') return '接口没有返回内容'
  if (typeof data === 'string') return TRACEBACK.test(data) ? '接口返回了内部错误，详细信息已隐藏' : data
  try {
    return JSON.stringify(data, (key, value) => SENSITIVE_KEY.test(key) ? '***' : value, 2)
  } catch {
    return '接口返回了无法解析的内容'
  }
}
