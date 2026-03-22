<!--
  TaskErrorCard.vue - 任务错误卡片组件
  
  功能说明：
  - 显示任务执行失败时的错误信息
  - 提供友好的错误提示
  - 提示用户可以采取的行动
  
  使用方式：
  <TaskErrorCard 
    message="具体的错误信息" 
    hint="用户可以做什么" 
  />
-->
<template>
  <article class="error-card">
    <!-- 卡片头部 -->
    <header class="error-card-header">
      <p class="error-card-eyebrow">Agent 输出</p>
      <h3 class="error-card-title">任务执行失败</h3>
    </header>

    <!-- 错误消息 -->
    <p class="error-card-message">{{ message }}</p>
    <!-- 错误提示（建议用户采取的行动） -->
    <p class="error-card-hint">{{ hint }}</p>
  </article>
</template>

<script setup lang="ts">
defineProps<{
  /** 具体错误信息 */
  message: string;
  /** 错误提示/建议 */
  hint: string;
}>();
</script>
