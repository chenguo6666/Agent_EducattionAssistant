<template>
  <div class="message-bubble" :class="role">
    <div class="message-role">{{ role === "user" ? "你" : "Agent" }}</div>
    <div class="message-content" v-html="html"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { renderMarkdown } from "@/components/markdown";

const props = defineProps<{
  role: "user" | "assistant";
  content: string;
}>();

const html = computed(() => renderMarkdown(props.content));
</script>
