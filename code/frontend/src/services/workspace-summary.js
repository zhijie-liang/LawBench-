export function getWorkspaceSummary(records = []) {
  const successCount = records.filter((record) => record.status === 'success').length
  return {
    total: records.length,
    questions: records.filter((record) => ['basic', 'graph', 'agent'].includes(record.type)).length,
    uploads: records.filter((record) => record.type === 'upload').length,
    successRate: records.length ? Math.round((successCount / records.length) * 100) : 0,
    serviceStatus: !records.length ? '等待验证' : records[0].status === 'success' ? '运行正常' : '需要检查',
  }
}

export function getRecommendedAction(records = []) {
  const uploaded = records.some((record) => record.type === 'upload' && record.status === 'success')
  if (!uploaded) return { title: '先完成资料入库', description: '上传 TXT 法律资料，建立本次问答依据。', path: '/workspace/upload', action: '前往资料入库' }
  const asked = records.some((record) => ['basic', 'graph', 'agent'].includes(record.type) && record.status === 'success')
  if (!asked) return { title: '开始流程问答', description: '资料已准备好，可以进行可追踪法律问答。', path: '/workspace/graph', action: '发起流程问答' }
  return { title: '查看本次运行结果', description: '问答已完成，可集中检查接口结果与运行状态。', path: '/workspace/records', action: '查看运行记录' }
}
