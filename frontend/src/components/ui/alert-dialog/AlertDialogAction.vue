<script setup>
import { AlertDialogAction } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps({ class: { type: String, default: '' } })
</script>

<template>
  <AlertDialogAction :class="cn('inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-zinc-900 text-zinc-50 hover:bg-zinc-900/90 h-10 px-4 py-2', props.class)">
    <slot />
  </AlertDialogAction>
</template>
