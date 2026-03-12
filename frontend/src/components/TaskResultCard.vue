<template>
  <article class="result-card">
    <header class="result-card-header">
      <div>
        <p class="result-card-eyebrow">Agent 输出</p>
        <h3 class="result-card-title">任务结果</h3>
      </div>
      <div class="result-actions">
        <span class="result-card-intent">{{ intentLabel }}</span>
        <button class="secondary-button compact-button" type="button" @click="$emit('export')">
          导出结果
        </button>
      </div>
    </header>

    <section v-if="result.answer" class="result-section">
      <div class="result-section-header">
        <h4>资料追问回答</h4>
      </div>
      <p class="result-summary">{{ result.answer }}</p>
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
              :class="{
                correct: submittedAnswers && optionLetter(optionIndex) === item.answer,
                selected: selectedAnswers[index] === optionLetter(optionIndex),
              }"
            >
              <button class="quiz-option-button" type="button" @click="selectAnswer(index, optionIndex)">
                <span>{{ optionLetter(optionIndex) }}.</span>
                <span>{{ option }}</span>
              </button>
            </li>
          </ul>
          <p v-if="submittedAnswers" class="quiz-answer">答案：{{ item.answer }}</p>
        </article>
      </div>

      <div class="quiz-submit-row">
        <button
          class="primary-button compact-button"
          type="button"
          :disabled="submittedAnswers || !allAnswered"
          @click="submitAnswers"
        >
          提交作答
        </button>
        <span v-if="quizFeedback" class="muted">{{ quizFeedback }}</span>
      </div>
    </section>

    <section v-if="sources.length" class="result-section">
      <div class="result-section-header">
        <h4>资料来源</h4>
        <span class="result-section-meta">{{ sources.length }} 段</span>
      </div>
      <div class="source-grid">
        <article v-for="source in sources" :key="source.chunkId" class="source-card">
          <div class="source-card-header">
            <strong>{{ source.fileName }}</strong>
            <span class="stage-pill">score {{ source.score.toFixed(1) }}</span>
          </div>
          <p>{{ source.content }}</p>
        </article>
      </div>
    </section>
  </article>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import type { ChatResult, RetrievedChunk } from "@/types/chat";

const props = defineProps<{
  intent: string;
  result: ChatResult;
  sources?: RetrievedChunk[];
  quizFeedback?: string;
}>();

const emit = defineEmits<{
  export: [];
  submitQuiz: [answers: Array<{ questionIndex: number; userAnswer: string }>];
}>();

const intentMap: Record<string, string> = {
  summary: "仅摘要",
  quiz: "仅出题",
  summary_and_quiz: "摘要 + 出题",
  rag_answer: "资料追问",
  unknown: "兜底处理",
};

const intentLabel = computed(() => intentMap[props.intent] ?? props.intent);
const sources = computed(() => props.sources ?? []);
const selectedAnswers = ref<Record<number, string>>({});
const submittedAnswers = ref(false);
const allAnswered = computed(() => {
  const quiz = props.result.quiz ?? [];
  return quiz.length > 0 && quiz.every((_, index) => Boolean(selectedAnswers.value[index]));
});

function optionLetter(index: number) {
  return String.fromCharCode(65 + index);
}

function selectAnswer(questionIndex: number, optionIndex: number) {
  if (submittedAnswers.value) {
    return;
  }
  selectedAnswers.value = {
    ...selectedAnswers.value,
    [questionIndex]: optionLetter(optionIndex),
  };
}

function submitAnswers() {
  if (!allAnswered.value || submittedAnswers.value) {
    return;
  }
  submittedAnswers.value = true;
  const answers = Object.entries(selectedAnswers.value).map(([questionIndex, userAnswer]) => ({
    questionIndex: Number(questionIndex),
    userAnswer,
  }));
  emit("submitQuiz", answers);
}
</script>
