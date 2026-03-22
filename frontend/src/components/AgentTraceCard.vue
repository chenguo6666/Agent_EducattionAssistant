<!--
  AgentTraceCard.vue - Agent 执行轨迹卡片组件
  
  功能说明：
  - 显示 AI Agent 执行任务的实时状态
  - 展示任务执行时间线（提交→分析→执行→完成/失败）
  - 展示 Agent 思考过程的轨迹（分析意图、调用工具、返回结果）
  - 展示工具调用的输入输出
  
  任务状态：
  - thinking: 思考中（初始状态）
  - submitted: 任务已提交
  - analyzing: 分析中
  - executing: 执行中
  - completed: 已完成
  - failed: 执行失败
  
  轨迹类型：
  - analysis: 分析任务意图
  - tool: 调用工具
  - final: 返回最终结果
-->
<template>
  <!-- 根据 loading 状态添加不同类名（加载中显示动画） -->
  <article class="agent-trace-card" :class="{ loading }">
    <!-- 卡片头部 -->
    <div class="agent-trace-header">
      <div>
        <!-- 加载中显示"思考中"，完成后显示"Agent 轨迹" -->
        <p class="agent-trace-eyebrow">{{ loading ? "思考中" : "Agent 轨迹" }}</p>
        <!-- 动态标题：加载中显示提示，完成后显示识别的意图 -->
        <h4 class="agent-trace-title">
          {{ loading ? "正在理解任务并准备调用工具" : traceTitle }}
        </h4>
      </div>
      <!-- 意图和状态标签 -->
      <div class="agent-trace-badges">
        <span v-if="intentLabel" class="trace-badge">{{ intentLabel }}</span>
        <span class="trace-badge" :class="statusClass">{{ statusLabel }}</span>
      </div>
    </div>

    <!-- 任务时间线（进度指示器） -->
    <div v-if="timeline.length > 0" class="agent-trace-timeline">
      <span
        v-for="stage in timeline"
        :key="`${stage.status}-${stage.label}`"
        class="trace-stage-pill"
        :class="stage.status"
      >
        {{ stage.label }}
      </span>
    </div>

    <!-- Agent 执行轨迹列表 -->
    <ul class="agent-trace-list">
      <li v-for="item in visibleTrace" :key="`${item.type}-${item.label}`" class="agent-trace-item">
        <!-- 状态指示器（圆点颜色表示状态） -->
        <span class="trace-item-status" :class="item.status"></span>
        <div class="trace-item-body">
          <strong>{{ item.label }}</strong>
          <p v-if="item.summary">{{ item.summary }}</p>
        </div>
      </li>
    </ul>

    <!-- 工具调用详情列表 -->
    <div v-if="toolCalls.length > 0" class="agent-tool-list">
      <article v-for="call in toolCalls" :key="call.toolName + call.inputSummary" class="agent-tool-card">
        <div class="agent-tool-head">
          <strong>{{ call.displayName }}</strong>
          <span class="trace-badge" :class="call.status">{{ toolStatusLabel(call.status) }}</span>
        </div>
        <p v-if="call.inputSummary">输入：{{ call.inputSummary }}</p>
        <p v-if="call.outputSummary">输出：{{ call.outputSummary }}</p>
      </article>
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { AgentTraceItem, TaskStage, TaskStatus, ToolCallItem, TraceStatus } from "@/types/chat";

const props = withDefaults(
  defineProps<{
    /** 任务意图（用于显示中文标签） */
    intent?: string;
    /** 当前任务状态 */
    status?: TaskStatus | "thinking";
    /** 任务执行时间线 */
    timeline?: TaskStage[];
    /** Agent 执行轨迹 */
    agentTrace?: AgentTraceItem[];
    /** 工具调用列表 */
    toolCalls?: ToolCallItem[];
    /** 是否处于加载中状态 */
    loading?: boolean;
  }>(),
  {
    intent: "",
    status: "thinking",
    timeline: () => [],
    agentTrace: () => [],
    toolCalls: () => [],
    loading: false,
  },
);

/**
 * 意图到中文标签的映射
 */
const intentMap: Record<string, string> = {
  assistant_chat: "自由对话",
  summary: "摘要",
  quiz: "出题",
  summary_and_quiz: "综合任务",
  key_points: "知识点提取",
  study_outline: "复习提纲",
  rag_answer: "资料追问",
  document_check: "资料确认",
  unknown: "待进一步分析",
};

/**
 * 状态到中文标签的映射
 */
const statusMap: Record<string, string> = {
  thinking: "思考中",
  submitted: "任务已提交",
  analyzing: "分析中",
  executing: "执行中",
  completed: "已完成",
  failed: "执行失败",
};

/** 意图中文标签 */
const intentLabel = computed(() => (props.intent ? intentMap[props.intent] ?? props.intent : ""));
/** 状态中文标签 */
const statusLabel = computed(() => statusMap[props.status] ?? "处理中");
/** 状态 CSS 类名 */
const statusClass = computed(() => props.status ?? "thinking");
/** 时间线（带默认值） */
const timeline = computed(() => props.timeline ?? []);
/** 工具调用（带默认值） */
const toolCalls = computed(() => props.toolCalls ?? []);

/**
 * 可见的轨迹列表
 * 如果有真实轨迹数据则使用，否则显示默认的加载中占位轨迹
 */
const visibleTrace = computed(() => {
  if (props.agentTrace.length > 0) {
    return props.agentTrace;
  }
  // 加载中的默认占位轨迹
  return [
    { type: "analysis", label: "任务已提交", status: "completed" as TraceStatus, summary: "消息已加入执行队列。" },
    { type: "tool", label: "分析用户需求", status: "running" as TraceStatus, summary: "正在识别任务类型与所需工具。" },
    { type: "final", label: "准备结果", status: "pending" as TraceStatus, summary: "等待工具执行完成后输出结果。" },
  ] as AgentTraceItem[];
});

/**
 * 计算轨迹标题
 * 有意图时显示"已识别为X"，否则显示默认提示
 */
const traceTitle = computed(() => {
  if (intentLabel.value) {
    return `已识别为${intentLabel.value}`;
  }
  return "正在生成执行轨迹";
});

/**
 * 工具调用状态的标签映射
 */
function toolStatusLabel(status: TraceStatus) {
  return {
    pending: "待执行",
    running: "执行中",
    completed: "已完成",
    failed: "失败",
  }[status];
}
</script>
