<script setup>
import { AlertDialogCancel } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps({ class: { type: String, default: '' } })
</script>

<template>
  <AlertDialogCancel :class="cn('inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-zinc-100 hover:text-accent-foreground h-10 px-4 py-2 mt-2 sm:mt-0', props.class)">
    <slot />
  </AlertDialogCancel>
</template>
