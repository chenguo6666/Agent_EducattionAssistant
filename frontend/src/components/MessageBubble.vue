<!--
  MessageBubble.vue - 消息气泡组件
  
  功能说明：
  - 渲染聊天消息（用户消息或助手消息）
  - 使用 Markdown 格式渲染内容
  - 区分用户和助手的显示样式
  
  使用方式：
  <MessageBubble role="user" content="用户输入" />
  <MessageBubble role="assistant" content="助手回复" />
-->
<template>
  <!-- 根据角色添加不同的 CSS 类（user 或 assistant） -->
  <div class="message-bubble" :class="role">
<<<<<<< HEAD
    <div class="message-role">{{ role === "user" ? "你" : "Agent" }}</div>
=======
    <!-- 角色标签 -->
    <div class="message-role">{{ role === "user" ? "You" : "Assistant" }}</div>
    <!-- 消息内容（Markdown 渲染后的 HTML） -->
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
    <div class="message-content" v-html="html"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { renderMarkdown } from "@/components/markdown";

const props = defineProps<{
  /** 消息角色：user（用户）或 assistant（助手） */
  role: "user" | "assistant";
  /** 消息内容（Markdown 格式） */
  content: string;
}>();

/**
 * 将 Markdown 内容转换为 HTML
 * 使用 computed 实现响应式：当 content 变化时自动重新渲染
 */
const html = computed(() => renderMarkdown(props.content));
</script>
