<!--
  TaskResultCard.vue - 任务结果卡片组件
  
  功能说明：
  - 显示 AI 任务执行的结果
  - 支持多种任务类型：摘要、练习题、问答回答
  - 展示资料来源片段
  - 支持选择题作答交互
  - 提供复制、导出、重新回答功能
  
  任务意图映射：
  - summary: 摘要
  - quiz: 出题
  - summary_and_quiz: 综合任务（摘要+出题）
  - rag_answer: 资料追问
  - key_points: 知识点提取
  - study_outline: 复习提纲
  - assistant_chat: 自由对话
-->
<template>
  <article class="result-card">
<<<<<<< HEAD
    <header class="result-card-header">
      <div>
        <p class="result-card-eyebrow">Agent 输出</p>
        <h3 class="result-card-title">任务结果</h3>
      </div>
=======
    <!-- 顶部操作栏：意图标签 + 操作按钮 -->
    <div class="result-actions result-actions-top">
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
      <span class="result-card-intent">{{ intentLabel }}</span>
    </header>

<<<<<<< HEAD
    <!-- 摘要结果 -->
    <section v-if="result.summary" class="result-section">
      <div class="result-section-header">
        <h4>摘要结果</h4>
      </div>
      <p class="result-summary">{{ result.summary }}</p>
    </section>

    <!-- 题目结果 -->
=======
    <!-- 问答回答 -->
    <section v-if="result.answer" class="result-section result-section-plain">
      <p class="result-summary">{{ result.answer }}</p>
    </section>

    <!-- 摘要内容 -->
    <section v-if="result.summary" class="result-section result-section-plain">
      <p class="result-summary">{{ result.summary }}</p>
    </section>

    <!-- 练习题区域 -->
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
    <section v-if="result.quiz?.length" class="result-section">
      <div class="result-section-header">
        <h4>题目结果</h4>
        <span class="result-section-meta">{{ result.quiz.length }} 题</span>
      </div>

      <!-- 题目列表 -->
      <div class="quiz-grid">
        <article v-for="(item, index) in result.quiz" :key="`${intent}-${index}`" class="quiz-card">
          <p class="quiz-index">题目 {{ index + 1 }}</p>
          <h5 class="quiz-question">{{ item.question }}</h5>
          
          <!-- 选项列表 -->
          <ul class="quiz-options">
            <li
              v-for="(option, optionIndex) in item.options"
              :key="`${index}-${optionIndex}`"
<<<<<<< HEAD
              :class="{ correct: optionLetter(optionIndex) === item.answer }"
=======
              :class="{
                correct: submittedAnswers && optionLetter(optionIndex) === item.answer,   // 正确答案高亮
                selected: selectedAnswers[index] === optionLetter(optionIndex),        // 用户选择的选项高亮
              }"
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
            >
              <span>{{ optionLetter(optionIndex) }}.</span>
              <span>{{ option }}</span>
            </li>
          </ul>
<<<<<<< HEAD
          <p class="quiz-answer">答案：{{ item.answer }}</p>
        </article>
      </div>
    </section>

    <!-- 翻译结果 -->
    <section v-if="result.translation" class="result-section">
=======
          
          <!-- 提交后显示正确答案 -->
          <p v-if="submittedAnswers" class="quiz-answer">答案：{{ item.answer }}</p>
        </article>
      </div>

      <!-- 提交按钮 -->
      <div class="quiz-submit-row">
        <button
          class="primary-button compact-button"
          type="button"
          :disabled="submittedAnswers || !allAnswered"
          @click="submitAnswers"
        >
          提交作答
        </button>
        <!-- 答题反馈（正确率等） -->
        <span v-if="quizFeedback" class="muted">{{ quizFeedback }}</span>
      </div>
    </section>

    <!-- 资料来源区域 -->
    <section v-if="sources.length" class="result-section">
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
      <div class="result-section-header">
        <h4>翻译结果</h4>
      </div>
<<<<<<< HEAD
      <div class="result-text-content" v-html="renderMarkdown(result.translation)"></div>
    </section>

    <!-- 润色结果 -->
    <section v-if="result.polish" class="result-section">
      <div class="result-section-header">
        <h4>润色结果</h4>
=======
      
      <!-- 来源片段列表 -->
      <div class="source-grid">
        <article v-for="source in sources" :key="source.chunkId" class="source-card">
          <div class="source-card-header">
            <strong>{{ source.fileName }}</strong>
            <span class="stage-pill">score {{ source.score.toFixed(1) }}</span>
          </div>
          <p>{{ source.content }}</p>
        </article>
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
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
  /** 任务意图（用于显示中文标签） */
  intent: string;
  /** 任务结果数据 */
  result: ChatResult;
<<<<<<< HEAD
=======
  /** 资料来源片段（可选） */
  sources?: RetrievedChunk[];
  /** 答题反馈消息（可选） */
  quizFeedback?: string;
}>();

// 定义组件可以触发的事件
const emit = defineEmits<{
  copy: [];      // 复制结果
  export: [];   // 导出结果
  retry: [];    // 重新回答
  /** 提交答题答案 */
  submitQuiz: [answers: Array<{ questionIndex: number; userAnswer: string }>];
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
}>();

/**
 * 意图到中文标签的映射表
 */
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

/** 意图中文标签（计算属性） */
const intentLabel = computed(() => intentMap[props.intent] ?? props.intent);
<<<<<<< HEAD
=======
/** 来源片段（带默认值） */
const sources = computed(() => props.sources ?? []);

/** 用户选择的答案 { 题目索引: 选择的字母 } */
const selectedAnswers = ref<Record<number, string>>({});
/** 是否已提交答案 */
const submittedAnswers = ref(false);

/**
 * 是否所有题目都已作答
 * 计算属性：检查 quiz 数组中每一题是否都有答案
 */
const allAnswered = computed(() => {
  const quiz = props.result.quiz ?? [];
  return quiz.length > 0 && quiz.every((_, index) => Boolean(selectedAnswers.value[index]));
});
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)

/**
 * 将数字索引转换为字母选项（A=0, B=1, C=2, D=3...）
 */
function optionLetter(index: number) {
  return String.fromCharCode(65 + index);
}

<<<<<<< HEAD
function renderMarkdown(text: string): string {
  return marked.parse(text) as string;
=======
/**
 * 选择答案
 * @param questionIndex - 题目索引
 * @param optionIndex - 选项索引
 */
function selectAnswer(questionIndex: number, optionIndex: number) {
  // 已提交则不能再修改
  if (submittedAnswers.value) {
    return;
  }
  selectedAnswers.value = {
    ...selectedAnswers.value,
    [questionIndex]: optionLetter(optionIndex),
  };
}

/**
 * 提交所有答案
 * 将答案格式化为 { questionIndex, userAnswer } 数组并触发事件
 */
function submitAnswers() {
  if (!allAnswered.value || submittedAnswers.value) {
    return;
  }
  submittedAnswers.value = true;
  
  // 转换为后端需要的格式
  const answers = Object.entries(selectedAnswers.value).map(([questionIndex, userAnswer]) => ({
    questionIndex: Number(questionIndex),
    userAnswer,
  }));
  
  emit("submitQuiz", answers);
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
}
</script>
