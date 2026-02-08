<script setup>
import { AlertDialogTrigger } from 'radix-vue'
</script>

<template>
  <AlertDialogTrigger v-bind="$attrs">
    <slot />
  </AlertDialogTrigger>
</template>
