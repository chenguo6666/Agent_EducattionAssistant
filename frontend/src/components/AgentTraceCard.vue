<template>
  <article class="agent-trace-card" :class="{ loading }">
    <div class="agent-trace-header">
      <div>
        <p class="agent-trace-eyebrow">{{ loading ? "思考中" : "Agent 轨迹" }}</p>
        <h4 class="agent-trace-title">
          {{ loading ? "正在理解任务并准备调用工具" : traceTitle }}
        </h4>
      </div>
      <div class="agent-trace-badges">
        <span v-if="intentLabel" class="trace-badge">{{ intentLabel }}</span>
        <span class="trace-badge" :class="statusClass">{{ statusLabel }}</span>
      </div>
    </div>

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

    <ul class="agent-trace-list">
      <li v-for="item in visibleTrace" :key="`${item.type}-${item.label}`" class="agent-trace-item">
        <span class="trace-item-status" :class="item.status"></span>
        <div class="trace-item-body">
          <strong>{{ item.label }}</strong>
          <p v-if="item.summary">{{ item.summary }}</p>
        </div>
      </li>
    </ul>

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
    intent?: string;
    status?: TaskStatus | "thinking";
    timeline?: TaskStage[];
    agentTrace?: AgentTraceItem[];
    toolCalls?: ToolCallItem[];
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

const statusMap: Record<string, string> = {
  thinking: "思考中",
  submitted: "任务已提交",
  analyzing: "分析中",
  executing: "执行中",
  completed: "已完成",
  failed: "执行失败",
};

const intentLabel = computed(() => (props.intent ? intentMap[props.intent] ?? props.intent : ""));
const statusLabel = computed(() => statusMap[props.status] ?? "处理中");
const statusClass = computed(() => props.status ?? "thinking");
const timeline = computed(() => props.timeline ?? []);
const toolCalls = computed(() => props.toolCalls ?? []);
const visibleTrace = computed(() => {
  if (props.agentTrace.length > 0) {
    return props.agentTrace;
  }
  return [
    { type: "analysis", label: "任务已提交", status: "completed", summary: "消息已加入执行队列。" },
    { type: "tool", label: "分析用户需求", status: "running", summary: "正在识别任务类型与所需工具。" },
    { type: "final", label: "准备结果", status: "pending", summary: "等待工具执行完成后输出结果。" },
  ] as AgentTraceItem[];
});
const traceTitle = computed(() => {
  if (intentLabel.value) {
    return `已识别为${intentLabel.value}`;
  }
  return "正在生成执行轨迹";
});

function toolStatusLabel(status: TraceStatus) {
  return {
    pending: "待执行",
    running: "执行中",
    completed: "已完成",
    failed: "失败",
  }[status];
}
</script>
