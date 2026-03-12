<template>
  <article class="result-card">
    <header class="result-card-header">
      <div>
        <p class="result-card-eyebrow">Agent 输出</p>
        <h3 class="result-card-title">任务结果</h3>
      </div>
      <div class="result-card-header-right">
        <span class="result-card-intent">{{ intentLabel }}</span>
        <div class="result-card-actions">
          <button class="secondary-button button-small" type="button" @click="copyMarkdown">复制 Markdown</button>
          <button class="secondary-button button-small" type="button" @click="copyText">复制纯文本</button>
          <button class="secondary-button button-small" type="button" @click="downloadMarkdown">下载 .md</button>
        </div>
      </div>
    </header>

    <section v-if="prompt" class="result-section result-prompt">
      <div class="result-section-header">
        <h4>任务输入</h4>
      </div>
      <p class="result-summary">{{ prompt }}</p>
    </section>

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
  prompt?: string;
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

function buildMarkdown() {
  const lines: string[] = [];
  lines.push(`# 任务结果`);
  lines.push("");
  lines.push(`- 意图：${intentLabel.value}`);

  if (props.prompt) {
    lines.push("");
    lines.push("## 任务输入");
    lines.push("");
    lines.push(props.prompt);
  }

  if (props.result.summary) {
    lines.push("");
    lines.push("## 摘要结果");
    lines.push("");
    lines.push(props.result.summary);
  }

  if (props.result.quiz?.length) {
    lines.push("");
    lines.push(`## 题目结果（${props.result.quiz.length} 题）`);
    lines.push("");

    props.result.quiz.forEach((item, index) => {
      lines.push(`${index + 1}. ${item.question}`);
      item.options.forEach((option, optionIndex) => {
        lines.push(`   - ${optionLetter(optionIndex)}. ${option}`);
      });
      lines.push(`   - 答案：${item.answer}`);
      lines.push("");
    });
  }

  return lines.join("\n");
}

function buildText() {
  const lines: string[] = [];
  lines.push("任务结果");
  lines.push(`意图：${intentLabel.value}`);
  if (props.prompt) {
    lines.push("");
    lines.push("任务输入：");
    lines.push(props.prompt);
  }
  if (props.result.summary) {
    lines.push("");
    lines.push("摘要结果：");
    lines.push(props.result.summary);
  }
  if (props.result.quiz?.length) {
    lines.push("");
    lines.push(`题目结果（${props.result.quiz.length} 题）：`);
    lines.push("");
    props.result.quiz.forEach((item, index) => {
      lines.push(`题目 ${index + 1}：${item.question}`);
      item.options.forEach((option, optionIndex) => {
        lines.push(`${optionLetter(optionIndex)}. ${option}`);
      });
      lines.push(`答案：${item.answer}`);
      lines.push("");
    });
  }
  return lines.join("\n");
}

async function writeClipboard(text: string) {
  try {
    await navigator.clipboard.writeText(text);
    return;
  } catch {
    // Fallback below.
  }

  const el = document.createElement("textarea");
  el.value = text;
  el.style.position = "fixed";
  el.style.left = "-9999px";
  el.style.top = "-9999px";
  document.body.appendChild(el);
  el.focus();
  el.select();
  try {
    document.execCommand("copy");
  } finally {
    document.body.removeChild(el);
  }
}

function copyMarkdown() {
  void writeClipboard(buildMarkdown());
}

function copyText() {
  void writeClipboard(buildText());
}

function downloadMarkdown() {
  const content = buildMarkdown();
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  const stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-");
  a.download = `education-agent-result-${stamp}.md`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
</script>
