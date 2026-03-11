<template>
  <article class="result-card">
    <header class="result-card-header">
      <div>
        <p class="result-card-eyebrow">Agent 输出</p>
        <h3 class="result-card-title">任务结果</h3>
      </div>
      <span class="result-card-intent">{{ intentLabel }}</span>
    </header>

    <section v-if="result.summary" class="result-section">
      <div class="result-section-header">
        <h4>摘要结果</h4>
      </div>
      <p class="result-summary">{{ result.summary }}</p>
    </section>

    <section v-if="result.quiz?.length" class="result-section">
      <div class="result-section-header">
        <h4>题目结果</h4>
        <span class="result-section-meta">{{ result.quiz.length }} 题</span>
      </div>

      <div class="quiz-grid">
        <article v-for="(item, index) in result.quiz" :key="`${intent}-${index}`" class="quiz-card">
          <p class="quiz-index">题目 {{ index + 1 }}</p>
          <h5 class="quiz-question">{{ item.question }}</h5>
          <ul class="quiz-options">
            <li
              v-for="(option, optionIndex) in item.options"
              :key="`${index}-${optionIndex}`"
              :class="{ correct: optionLetter(optionIndex) === item.answer }"
            >
              <span>{{ optionLetter(optionIndex) }}.</span>
              <span>{{ option }}</span>
            </li>
          </ul>
          <p class="quiz-answer">答案：{{ item.answer }}</p>
        </article>
      </div>
    </section>
  </article>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { ChatResult } from "@/types/chat";

const props = defineProps<{
  intent: string;
  result: ChatResult;
}>();

const intentMap: Record<string, string> = {
  summary: "仅摘要",
  quiz: "仅出题",
  summary_and_quiz: "摘要 + 出题",
  unknown: "兜底处理",
};

const intentLabel = computed(() => intentMap[props.intent] ?? props.intent);

function optionLetter(index: number) {
  return String.fromCharCode(65 + index);
}
</script>
