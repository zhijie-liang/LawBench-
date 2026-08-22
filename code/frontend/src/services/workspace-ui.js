export function filterRecords(records, type = 'all', status = 'all') {
  return records.filter((record) => (type === 'all' || record.type === type) && (status === 'all' || record.status === status))
}

export function getUploadPhase({ file = null, loading = false, notice = '', error = '' } = {}) {
  if (error) return 'error'
  if (notice) return 'success'
  if (loading) return 'processing'
  if (file) return 'ready'
  return 'select'
}
