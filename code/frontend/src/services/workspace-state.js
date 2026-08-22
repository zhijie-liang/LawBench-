import { createModeState } from './mode-state.js'

const WORKSPACE_KEY = 'lawbench-v2-workspace-state'

function normalizeModeState(value) {
  const fallback = createModeState()
  return {
    messages: Array.isArray(value?.messages) && value.messages.length ? value.messages : fallback.messages,
    evidence: {
      answer: value?.evidence?.answer || '',
      contexts: Array.isArray(value?.evidence?.contexts) ? value.evidence.contexts : [],
      trace: Array.isArray(value?.evidence?.trace) ? value.evidence.trace : [],
      stage: value?.evidence?.stage || '',
    },
    lastResponse: value?.lastResponse ?? null,
    lastLabel: value?.lastLabel || '',
  }
}

export function createWorkspaceState() {
  return { basic: createModeState(), graph: createModeState(), records: [] }
}

export function loadWorkspaceState() {
  try {
    const value = JSON.parse(sessionStorage.getItem(WORKSPACE_KEY) || 'null')
    if (!value || typeof value !== 'object') return createWorkspaceState()
    return {
      basic: normalizeModeState(value.basic),
      graph: normalizeModeState(value.graph),
      records: Array.isArray(value.records) ? value.records : [],
    }
  } catch {
    return createWorkspaceState()
  }
}

export function saveWorkspaceState(state) {
  try {
    sessionStorage.setItem(WORKSPACE_KEY, JSON.stringify(state))
    return true
  } catch {
    return false
  }
}

export function clearWorkspaceState() {
  sessionStorage.removeItem(WORKSPACE_KEY)
}
