import { reactive, watch } from 'vue'
import { createModeState } from '../services/mode-state.js'
import { clearWorkspaceState, createWorkspaceState, loadWorkspaceState, saveWorkspaceState } from '../services/workspace-state.js'

export const workspaceState = reactive(loadWorkspaceState())

watch(workspaceState, (state) => saveWorkspaceState(state), { deep: true })

export function addRecord({ type, label, response, status = 'success' }) {
  workspaceState.records.unshift({
    id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    type,
    label,
    response,
    status,
    time: new Date().toLocaleString('zh-CN', { hour12: false }),
  })
}

export function clearMode(mode) {
  workspaceState[mode] = createModeState()
}

export function resetWorkspaceStore() {
  const fresh = createWorkspaceState()
  workspaceState.basic = fresh.basic
  workspaceState.graph = fresh.graph
  workspaceState.records = fresh.records
  clearWorkspaceState()
}
