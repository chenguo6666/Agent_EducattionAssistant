<template>
  <article class="result-card">
    <header class="result-card-header">
      <div>
        <p class="result-card-eyebrow">Agent 输出</p>
        <h3 class="result-card-title">任务结果</h3>
      </div>
      <span class="result-card-intent">{{ intentLabel }}</span>
    </header>

    <!-- 摘要结果 -->
    <section v-if="result.summary" class="result-section">
      <div class="result-section-header">
        <h4>摘要结果</h4>
      </div>
      <p class="result-summary">{{ result.summary }}</p>
    </section>

    <!-- 题目结果 -->
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

    <!-- 翻译结果 -->
    <section v-if="result.translation" class="result-section">
      <div class="result-section-header">
        <h4>翻译结果</h4>
      </div>
      <div class="result-text-content" v-html="renderMarkdown(result.translation)"></div>
    </section>

    <!-- 润色结果 -->
    <section v-if="result.polish" class="result-section">
      <div class="result-section-header">
        <h4>润色结果</h4>
      </div>
      <div class="result-text-content" v-html="renderMarkdown(result.polish)"></div>
    </section>

    <!-- 解释结果 -->
    <section v-if="result.explanation" class="result-section">
      <div class="result-section-header">
        <h4>词义解释</h4>
      </div>
      <div class="result-text-content" v-html="renderMarkdown(result.explanation)"></div>
    </section>

    <!-- 对比分析结果 -->
    <section v-if="result.comparison" class="result-section">
      <div class="result-section-header">
        <h4>对比分析</h4>
      </div>
      <div class="result-text-content" v-html="renderMarkdown(result.comparison)"></div>
    </section>
  </article>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { marked } from "marked";
import type { ChatResult } from "@/types/chat";

const props = defineProps<{
  intent: string;
  result: ChatResult;
}>();

const intentMap: Record<string, string> = {
  summary: "文本摘要",
  quiz: "选择题生成",
  summary_and_quiz: "摘要 + 出题",
  translation: "翻译",
  polish: "内容润色",
  explanation: "词义解释",
  comparison: "对比分析",
  unknown: "兜底处理",
};

const intentLabel = computed(() => intentMap[props.intent] ?? props.intent);

function optionLetter(index: number) {
  return String.fromCharCode(65 + index);
}

function renderMarkdown(text: string): string {
  return marked.parse(text) as string;
}
</script>
