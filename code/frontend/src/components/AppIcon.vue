<script setup>
defineProps({ name: { type: String, required: true }, size: { type: Number, default: 18 } })
</script>

<template>
  <svg class="app-icon" :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <template v-if="name === 'overview'"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></template>
    <template v-else-if="name === 'chat'"><path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z"/><path d="M8 9h8M8 13h5"/></template>
    <template v-else-if="name === 'workflow'"><circle cx="6" cy="6" r="2"/><circle cx="18" cy="6" r="2"/><circle cx="12" cy="18" r="2"/><path d="M8 6h8M7.4 7.5l3.4 8.7M16.6 7.5l-3.4 8.7"/></template>
    <template v-else-if="name === 'agent'"><path d="M12 3v4M12 17v4M3 12h4M17 12h4"/><circle cx="12" cy="12" r="4"/><path d="m5.6 5.6 2.8 2.8m7.2 7.2 2.8 2.8m0-12.8-2.8 2.8m-7.2 7.2-2.8 2.8"/></template>
    <template v-else-if="name === 'upload'"><path d="M12 16V3M7 8l5-5 5 5"/><path d="M4 15v4a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-4"/></template>
    <template v-else-if="name === 'history'"><path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5M12 7v5l3 2"/></template>
    <template v-else-if="name === 'shield'"><path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11z"/><path d="m9 12 2 2 4-5"/></template>
    <template v-else-if="name === 'logout'"><path d="M10 17l5-5-5-5M15 12H3"/><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/></template>
    <template v-else-if="name === 'file'"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h6"/></template>
    <template v-else-if="name === 'send'"><path d="m22 2-7 20-4-9-9-4zM22 2 11 13"/></template>
    <template v-else-if="name === 'check'"><path d="m20 6-11 11-5-5"/></template>
    <template v-else-if="name === 'alert'"><path d="M10.3 2.9 1.8 17a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 2.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/></template>
    <template v-else><circle cx="12" cy="12" r="9"/><path d="M12 8v4l3 2"/></template>
  </svg>
</template>
