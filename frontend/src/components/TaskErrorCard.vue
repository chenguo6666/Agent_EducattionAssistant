<template>
  <article class="error-card">
    <header class="error-card-header">
      <p class="error-card-eyebrow">Assistant</p>
      <h3 class="error-card-title">任务执行失败</h3>
    </header>

    <p class="error-card-message">{{ message }}</p>
    <p class="error-card-hint">{{ hint }}</p>
  </article>
</template>

<script setup lang="ts">
defineProps<{
  message: string;
  hint: string;
}>();
</script>
