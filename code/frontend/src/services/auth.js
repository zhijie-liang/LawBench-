const AUTH_KEY = 'lawbench-v2-user'
export function setAuthenticated(username) { sessionStorage.setItem(AUTH_KEY, username) }
export function isAuthenticated() { return Boolean(sessionStorage.getItem(AUTH_KEY)) }
export function currentUser() { return sessionStorage.getItem(AUTH_KEY) || '' }
export function clearAuth() { sessionStorage.removeItem(AUTH_KEY) }
