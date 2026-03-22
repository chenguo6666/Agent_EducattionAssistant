<<<<<<< HEAD
﻿<template>
  <main class="chat-layout">
    <ToastNotification
      :visible="toastVisible"
      :message="toastMessage"
      :type="toastType"
      @close="toastVisible = false"
    />
    
    <aside class="sidebar-card">
      <p class="eyebrow">教育场景 Agent</p>
      <h1>对话工作台</h1>
      <p class="muted">当前阶段先验证 Sprint 1 主链路：输入任务、识别意图、调用 Mock Tool、返回结果。</p>

      <div class="status-panel hero-status-panel">
        <div>
=======
<!--
  ChatPage.vue - 聊天主页面组件
  
  功能说明：
  这是教育助手 AI Agent 的核心页面，包含三大区域：
  
  1. 侧边栏 (sidebar)
     - 历史会话列表（点击切换会话）
     - 最近错题本（答题错误自动记录）
     - 用户信息和退出登录
  
  2. 主聊天区 (chat-card)
     - 消息列表（用户消息、助手消息、任务轨迹、任务结果、错误提示）
     - 顶部标题栏（显示当前会话信息）
  
  3. 底部输入区 (composer)
     - 消息输入框
     - 文件上传按钮（支持 txt/md/pdf/docx）
     - 快捷任务模板选择
     - 发送按钮和重新回答按钮
  
  消息类型系统：
  - text: 普通文本消息（用户输入或助手回复）
  - trace: 任务执行轨迹（显示 Agent 执行状态和工具调用）
  - result: 任务结果（显示摘要/题目/问答结果）
  - error: 错误提示
  
  会话管理：
  - 支持多会话（每个会话独立的历史记录和资料）
  - 新建会话会清空当前聊天
  - 上传资料自动关联到当前会话
-->
<template>
  <main class="chat-layout chatgpt-shell" :class="{ 'sidebar-open': isSidebarOpen }">
    <!-- 移动端：侧边栏打开时的遮罩层 -->
    <button v-if="!isSidebarOpen" class="sidebar-toggle floating-toggle" type="button" @click="toggleSidebar">
      菜单
    </button>
    <div v-if="isSidebarOpen" class="sidebar-backdrop" @click="closeSidebar"></div>

    <!-- ============ 侧边栏 ============ -->
    <aside class="sidebar-card chatgpt-sidebar" :class="{ open: isSidebarOpen }">
      <div class="sidebar-top">
        <!-- 侧边栏工具栏 -->
        <div class="sidebar-toolbar">
          <button class="secondary-button sidebar-new-chat" type="button" @click="startNewSession">+ 新建对话</button>
          <button class="icon-action-button sidebar-close" type="button" @click="closeSidebar">收起</button>
        </div>

        <!-- 历史会话列表 -->
        <section class="sidebar-section">
          <p class="sidebar-section-title">历史会话</p>
          <p v-if="sessionError" class="inline-feedback">{{ sessionError }}</p>
          <div v-if="loadingSessions" class="session-empty">正在加载会话...</div>
          <div v-else-if="sessions.length === 0" class="session-empty">还没有历史会话，直接提问即可创建。</div>
          <div v-else class="session-list">
            <button
              v-for="session in sessions"
              :key="session.sessionId"
              class="session-item"
              :class="{ active: session.sessionId === activeSessionId }"
              type="button"
              @click="openSession(session.sessionId)"
            >
              <strong>{{ session.title }}</strong>
              <span>{{ session.lastMessage || "暂无消息" }}</span>
              <small>{{ formatSessionTime(session.updatedAt) }}</small>
            </button>
          </div>
        </section>

        <!-- 最近错题 -->
        <section class="sidebar-section">
          <div class="session-panel-header">
            <p class="sidebar-section-title">最近错题</p>
            <span class="muted">{{ mistakes.length }} 条</span>
          </div>
          <div v-if="mistakes.length === 0" class="session-empty">提交选择题作答后，错题会显示在这里。</div>
          <div v-else class="mistake-list compact-list">
            <article v-for="mistake in mistakes" :key="mistake.id" class="mistake-item">
              <strong>{{ mistake.question }}</strong>
              <p>你的答案：{{ mistake.userAnswer }}，正确答案：{{ mistake.correctAnswer }}</p>
              <small v-if="mistake.sourceExcerpt">{{ mistake.sourceExcerpt }}</small>
            </article>
          </div>
        </section>
      </div>

      <!-- 侧边栏底部：用户信息 -->
      <div class="sidebar-bottom">
        <div class="sidebar-meta">
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
          <span class="status-label">当前用户</span>
          <strong>{{ authStore.username || "未命名用户" }}</strong>
        </div>
        <div>
          <span class="status-label">任务状态</span>
          <strong>{{ currentStatusLabel }}</strong>
        </div>
        <div>
          <span class="status-label">识别意图</span>
          <strong>{{ intent || "等待提交" }}</strong>
        </div>
      </div>

      <div>
        <p class="status-label">Agent 阶段</p>
        <div class="stage-list">
          <article
            v-for="stage in stageCards"
            :key="stage.status"
            class="stage-card"
            :class="stage.stateClass"
          >
            <div class="stage-card-header">
              <strong>{{ stage.title }}</strong>
              <span class="stage-pill">{{ stage.stateLabel }}</span>
            </div>
            <p class="stage-card-detail">{{ stage.detail }}</p>
          </article>
        </div>
      </div>

      <div>
        <p class="status-label">执行计划</p>
        <ul class="step-list">
          <li v-for="step in planSteps" :key="step">{{ step }}</li>
          <li v-if="planSteps.length === 0">等待任务分析</li>
        </ul>
      </div>

      <button class="secondary-button" type="button" @click="logout">退出登录</button>
    </aside>

<<<<<<< HEAD
    <section class="chat-card">
      <div class="message-list">
        <template v-for="message in messages" :key="message.id">
          <MessageBubble
            v-if="message.kind === 'text'"
            :role="message.role"
            :content="message.content ?? ''"
          />
=======
    <!-- ============ 主聊天区 ============ -->
    <section class="chat-card chatgpt-main">
      <!-- 顶部标题栏 -->
      <header class="chatgpt-header compact-topbar">
        <div class="topbar-title">
          <button class="icon-action-button sidebar-toggle-inline" type="button" @click="toggleSidebar">菜单</button>
          <strong>Education Assistant</strong>
          <span class="muted">{{ activeSessionTitle }}</span>
        </div>
        <div class="header-badges">
          <span class="stage-pill">{{ documents.length > 0 ? `${documents.length} 份资料` : "自由聊天" }}</span>
        </div>
      </header>

      <!-- 消息列表 -->
      <div ref="messageListRef" class="message-list chatgpt-message-list">
        <div v-if="loadingHistory" class="chat-area-empty">正在加载对话内容...</div>
        
        <!-- 渲染所有消息 -->
        <template v-else v-for="message in messages" :key="message.id">
          <!-- 普通文本消息 -->
          <MessageBubble v-if="message.kind === 'text'" :role="message.role" :content="message.content ?? ''" />

          <!-- 任务执行轨迹 -->
          <AgentTraceCard
            v-else-if="message.kind === 'trace'"
            :intent="message.intent"
            :status="message.status"
            :timeline="message.timeline"
            :agent-trace="message.agentTrace"
            :tool-calls="message.toolCalls"
            :loading="message.loading"
          />

          <!-- 任务结果 -->
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
          <TaskResultCard
            v-else-if="message.kind === 'result'"
            :intent="message.intent ?? 'unknown'"
            :result="message.result!"
          />
<<<<<<< HEAD
          <TaskErrorCard
            v-else
            :message="message.errorMessage ?? '请求失败'"
            :hint="message.errorHint ?? '请检查任务描述后重试。'"
=======

          <!-- 错误提示 -->
          <TaskErrorCard
            v-else
            :message="message.errorMessage ?? '请求失败'"
            :hint="message.errorHint ?? '请检查输入后重试.'"
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
          />
        </template>
      </div>

<<<<<<< HEAD
      <form class="chat-form" @submit.prevent="handleSubmit">
        <div class="template-panel">
          <div class="template-panel-header">
            <p class="status-label">预设任务模板</p>
            <span class="muted">点击后自动填充输入框</span>
          </div>
          <div class="template-grid">
            <button
              v-for="template in presetTemplates"
              :key="template.label"
              class="template-chip"
              type="button"
              @click="applyTemplate(template.prompt)"
            >
              <strong>{{ template.label }}</strong>
              <span>{{ template.description }}</span>
            </button>
=======
      <!-- ============ 底部输入区 ============ -->
      <div class="chatgpt-composer-wrap">
        <form class="chat-form chatgpt-form compact-composer" @submit.prevent="handleSubmit">
          <!-- 反馈信息 -->
          <p v-if="composerNotice" class="inline-feedback success">{{ composerNotice }}</p>
          <p v-if="composerError" class="inline-feedback">{{ composerError }}</p>

          <!-- 工具栏 -->
          <div class="composer-controls">
            <div class="composer-toolbar">
              <!-- 文件上传按钮 -->
              <label class="icon-action-button composer-add-button" :class="{ loading: uploadingDocument }">
                <span>{{ uploadingDocument ? "..." : "+" }}</span>
                <input
                  class="file-input"
                  type="file"
                  accept=".txt,.md,.pdf,.docx"
                  :disabled="uploadingDocument"
                  @change="handleFileChange"
                />
              </label>
              
              <!-- 快捷任务模板选择 -->
              <select v-model="selectedTemplate" class="template-select" @change="handleTemplateSelect">
                <option value="">快捷任务</option>
                <option v-for="template in presetTemplates" :key="template.label" :value="template.label">
                  {{ template.label }}
                </option>
              </select>
            </div>

            <!-- 当前会话的资料列表 -->
            <div v-if="documents.length > 0" class="composer-document-row">
              <span class="composer-document-label">资料</span>
              <div class="composer-document-list">
                <span v-for="document in documents" :key="document.documentId" class="composer-document-chip">
                  {{ document.fileName }}
                </span>
              </div>
            </div>
          </div>

          <!-- 消息输入框（自动高度） -->
          <textarea
            v-model="draft"
            rows="1"
            placeholder="有问题，尽管问"
            :disabled="submitting || checkingSession || loadingHistory"
          />

          <!-- 操作按钮栏 -->
          <div class="chat-actions">
            <span class="muted">支持自由对话、资料追问、摘要生成、题目生成和结果导出。</span>
            <div class="chat-action-buttons">
              <button v-if="canRetryLastTask" class="secondary-button compact-button" type="button" @click="retryLastTask">
                重新回答
              </button>
              <button class="primary-button compact-send-button" type="submit" :disabled="submitting || checkingSession || loadingHistory">
                {{ checkingSession ? "校验中..." : submitting ? "思考中..." : "发送" }}
              </button>
            </div>
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
          </div>
        </div>

        <p v-if="composerError" class="inline-feedback">{{ composerError }}</p>
        <textarea
          v-model="draft"
          rows="5"
          placeholder="例如：总结这篇历史课文并生成 5 个选择题"
        />
        <div class="chat-actions">
          <span class="muted">支持中文自然语言任务输入</span>
          <div class="chat-action-buttons">
            <button
              v-if="canRetryLastTask"
              class="secondary-button"
              type="button"
              @click="retryLastTask"
            >
              重试上次任务
            </button>
            <button class="primary-button" type="submit" :disabled="submitting || checkingSession">
              {{ checkingSession ? "校验登录中..." : submitting ? "处理中..." : "发送任务" }}
            </button>
          </div>
        </div>
      </form>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { fetchMe } from "@/api/auth";
import { executeTask } from "@/api/chat";
import MessageBubble from "@/components/MessageBubble.vue";
import TaskErrorCard from "@/components/TaskErrorCard.vue";
import TaskResultCard from "@/components/TaskResultCard.vue";
import ToastNotification from "@/components/ToastNotification.vue";
import { useAuthStore } from "@/stores/auth";
<<<<<<< HEAD
import type { ChatResponse, ChatResult, TaskStage, TaskStatus } from "@/types/chat";

type MessageKind = "text" | "result" | "error";
=======
import type {
  AgentTraceItem,
  ChatResponse,
  ChatResult,
  ChatSessionSummary,
  DocumentSummary,
  MistakeItem,
  RetrievedChunk,
  TaskRecord,
  TaskStage,
  TaskStatus,
  ToolCallItem,
} from "@/types/chat";

// ==================== 类型定义 ====================

/** 消息类型枚举 */
type MessageKind = "text" | "trace" | "result" | "error";

/**
 * 消息项接口
 * 
 * 统一的消息数据结构，支持多种消息类型：
 * - text: 普通文本消息
 * - trace: 任务执行轨迹
 * - result: 任务结果
 * - error: 错误提示
 */
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
interface MessageItem {
  /** 唯一标识 */
  id: string;
  /** 消息角色 */
  role: "user" | "assistant";
  /** 消息类型 */
  kind: MessageKind;
<<<<<<< HEAD
  content?: string;
  result?: ChatResult;
  intent?: string;
=======
  /** 任务记录 ID（result 类型需要） */
  recordId?: number;
  /** 消息内容（text 类型） */
  content?: string;
  /** 用户输入的提示（用于重新回答） */
  prompt?: string;
  /** 任务结果（result 类型） */
  result?: ChatResult;
  /** 资料来源（result 类型） */
  sources?: RetrievedChunk[];
  /** 答题反馈（result 类型） */
  quizFeedback?: string;
  /** 任务意图（trace 类型） */
  intent?: string;
  /** 任务状态（trace 类型） */
  status?: TaskStatus | "thinking";
  /** 时间线（trace 类型） */
  timeline?: TaskStage[];
  /** Agent 轨迹（trace 类型） */
  agentTrace?: AgentTraceItem[];
  /** 工具调用（trace 类型） */
  toolCalls?: ToolCallItem[];
  /** 是否加载中（trace 类型） */
  loading?: boolean;
  /** 错误消息（error 类型） */
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
  errorMessage?: string;
  /** 错误提示（error 类型） */
  errorHint?: string;
}

// ==================== 组件实例 ====================

const router = useRouter();
const authStore = useAuthStore();

<<<<<<< HEAD
// Toast state
const toastVisible = ref(false);
const toastMessage = ref("");
const toastType = ref<"success" | "error" | "info">("info");

const draft = ref("总结这篇历史课文并生成 5 个选择题：工业革命促进了生产力发展，也带来了社会结构的变化。");
const submitting = ref(false);
const checkingSession = ref(true);
const status = ref<TaskStatus | "idle">("idle");
const intent = ref("");
const planSteps = ref<string[]>([]);
const currentStatusLabel = ref("等待提交");
const progressTimers: number[] = [];
const composerError = ref("");
const lastSubmittedMessage = ref("");
const messages = ref<MessageItem[]>([
  {
    id: "welcome",
    role: "assistant",
    kind: "text",
    content: "### 欢迎\n\n你可以直接输入学习任务，我会先按 Sprint 1 的能力返回摘要、题目或综合结果。",
  },
]);
=======
// ==================== 响应式状态 ====================

/** 侧边栏是否打开（大屏默认打开，小屏默认关闭） */
const isSidebarOpen = ref(window.innerWidth > 1080);
/** 消息输入草稿 */
const draft = ref("");
/** 选中的快捷模板 */
const selectedTemplate = ref("");
/** 是否正在提交消息 */
const submitting = ref(false);
/** 是否正在上传文件 */
const uploadingDocument = ref(false);
/** 是否正在校验会话（页面初始化时） */
const checkingSession = ref(true);
/** 是否正在加载会话列表 */
const loadingSessions = ref(false);
/** 是否正在加载历史消息 */
const loadingHistory = ref(false);
/** 错误消息 */
const composerError = ref("");
/** 通知消息 */
const composerNotice = ref("");
/** 最后提交的消息（用于重新回答） */
const lastSubmittedMessage = ref("");
/** 会话列表加载错误 */
const sessionError = ref("");

/** 历史会话列表 */
const sessions = ref<ChatSessionSummary[]>([]);
/** 当前会话关联的文档列表 */
const documents = ref<DocumentSummary[]>([]);
/** 错题列表 */
const mistakes = ref<MistakeItem[]>([]);
/** 当前活跃会话 ID */
const activeSessionId = ref("");
/** 当前会话标题 */
const activeSessionTitle = ref("新对话");
/** 消息列表 */
const messages = ref<MessageItem[]>(createWelcomeMessages());
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)

// ==================== 快捷任务模板 ====================

/**
 * 预设的任务模板
 * 用户可以从下拉框选择快速填写输入框
 */
const presetTemplates = [
  {
    label: "总结 + 出题",
    description: "适合历史、语文、政治类材料",
    prompt: "请总结这段学习材料，并生成 5 个选择题帮助我复习：",
  },
  {
    label: "提取知识点",
    description: "把长文本压缩成复习要点",
    prompt: "请提取这段内容的核心知识点，并按条目列出：",
  },
  {
    label: "生成复习提纲",
    description: "适合课前预习和考前梳理",
    prompt: "请根据这段内容生成一份结构化复习提纲：",
  },
  {
    label: "中英翻译",
    description: "中英文互译，支持学术词汇",
    prompt: "请将以下内容翻译成英文：",
  },
  {
    label: "文本摘要",
    description: "将长文本压缩为简短摘要",
    prompt: "请为以下内容生成一个简洁的摘要（50字以内）：",
  },
  {
    label: "内容润色",
    description: "改进表达，使内容更流畅",
    prompt: "请帮我润色以下内容，使表达更加准确流畅：",
  },
  {
    label: "词义解释",
    description: "解释专业术语或成语含义",
    prompt: "请解释以下词语的含义并给出例句：",
  },
  {
    label: "对比分析",
    description: "对比分析两个概念或事物",
    prompt: "请对比分析以下两个概念的区别与联系：",
  },
];

<<<<<<< HEAD
const stageLabelMap: Record<TaskStatus, string> = {
  submitted: "任务已提交",
  analyzing: "分析中",
  executing: "执行中",
  completed: "已完成",
  failed: "执行失败",
};

const orderedStages: TaskStatus[] = ["submitted", "analyzing", "executing", "completed"];
const stageTitleMap: Record<TaskStatus, string> = {
  submitted: "任务提交",
  analyzing: "意图分析",
  executing: "工具执行",
  completed: "结果整理",
  failed: "执行失败",
};
const defaultStageDetails: Record<TaskStatus, string> = {
  submitted: "前端已接收并提交任务，准备交给后端处理。",
  analyzing: "系统正在理解你的任务意图，并决定是否需要多个工具协作。",
  executing: "系统正在调用摘要工具、出题工具或组合流程。",
  completed: "结果已经整理完成，可以在对话区查看输出内容。",
  failed: "本次任务执行失败，请检查输入或重试。",
};

const stageCards = computed(() => {
  const currentIndex = status.value === "idle" ? -1 : orderedStages.indexOf(status.value as TaskStatus);

  return orderedStages.map((stageStatus, index) => {
    let stateClass = "pending";
    let stateLabel = "待执行";

    if (status.value === "failed") {
      if (index < 2) {
        stateClass = "completed";
        stateLabel = "已完成";
      } else if (stageStatus === "executing") {
        stateClass = "failed";
        stateLabel = "失败";
      }
    } else if (currentIndex > index) {
      stateClass = "completed";
      stateLabel = "已完成";
    } else if (currentIndex === index) {
      stateClass = "active";
      stateLabel = stageStatus === "completed" ? "已完成" : "进行中";
    }

    return {
      status: stageStatus,
      title: stageTitleMap[stageStatus],
      detail: defaultStageDetails[stageStatus],
      stateClass,
      stateLabel,
    };
=======
// ==================== 计算属性 ====================

/** 是否可以重新回答上一条消息 */
const canRetryLastTask = computed(() => Boolean(lastSubmittedMessage.value) && !submitting.value);

// ==================== 消息创建函数 ====================

/**
 * 创建欢迎消息（初始状态显示）
 */
function createWelcomeMessages(): MessageItem[] {
  return [
    {
      id: "welcome",
      role: "assistant",
      kind: "text",
      content: "你好，我可以直接和你对话，也可以在上传资料后帮助你做总结、出题、提取知识点、生成提纲和资料追问。",
    },
  ];
}

/**
 * 创建待处理的轨迹消息（刚发送消息时显示）
 */
function createPendingTrace(prompt: string): MessageItem {
  return {
    id: `trace-${crypto.randomUUID()}`,
    role: "assistant",
    kind: "trace",
    prompt,
    status: "thinking",
    loading: true,
    // 默认时间线
    timeline: [
      { status: "submitted", label: "任务已提交" },
      { status: "analyzing", label: "分析中" },
      { status: "executing", label: "执行中" },
    ],
    agentTrace: [],
    toolCalls: [],
  };
}

/**
 * 从 API 响应创建轨迹消息
 */
function createTraceFromResponse(response: ChatResponse, prompt: string): MessageItem {
  return {
    id: `trace-record-${response.recordId}`,
    role: "assistant",
    kind: "trace",
    prompt,
    intent: response.intent,
    status: response.status,
    timeline: response.timeline,
    agentTrace: response.agentTrace,
    toolCalls: response.toolCalls,
    loading: false,
  };
}

/**
 * 从任务记录创建轨迹消息（历史加载）
 */
function createTraceFromTask(task: TaskRecord): MessageItem {
  return {
    id: `trace-record-${task.id}`,
    role: "assistant",
    kind: "trace",
    prompt: task.message,
    intent: task.intent,
    status: task.status,
    timeline: task.timeline,
    agentTrace: task.agentTrace,
    toolCalls: task.toolCalls,
    loading: false,
  };
}

/**
 * 创建失败的轨迹消息
 */
function createFailedTrace(prompt: string, messageText: string): MessageItem {
  return {
    id: `trace-error-${crypto.randomUUID()}`,
    role: "assistant",
    kind: "trace",
    prompt,
    status: "failed",
    loading: false,
    timeline: [
      { status: "submitted", label: "任务已提交" },
      { status: "analyzing", label: "分析中" },
      { status: "failed", label: "任务失败" },
    ],
    agentTrace: [
      { type: "analysis", label: "识别任务意图", status: "completed", summary: "已开始分析用户需求。" },
      { type: "final", label: "返回错误结果", status: "failed", summary: messageText },
    ],
    toolCalls: [],
  };
}

/**
 * 替换消息（用于更新待处理消息为实际响应）
 */
function replaceMessage(messageId: string, nextMessage: MessageItem) {
  const index = messages.value.findIndex((item) => item.id === messageId);
  if (index === -1) {
    messages.value.push(nextMessage);
    return;
  }
  messages.value.splice(index, 1, nextMessage);
}

// ==================== UI 状态管理 ====================

/** 重置反馈状态 */
function resetFeedback() {
  composerError.value = "";
  composerNotice.value = "";
}

/** 切换侧边栏 */
function toggleSidebar() {
  isSidebarOpen.value = !isSidebarOpen.value;
}

/** 关闭侧边栏 */
function closeSidebar() {
  isSidebarOpen.value = false;
}

/**
 * 滚动到底部
 * 在消息更新后调用，确保最新消息可见
 */
async function scrollToBottom() {
  await nextTick();
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight;
  }
}

/**
 * 格式化会话时间
 * @param value - ISO 时间字符串
 * @returns 格式化的日期时间字符串（如 "3月22日 14:30"）
 */
function formatSessionTime(value: string) {
  return new Date(value).toLocaleString("zh-CN", {
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
  });
});

<<<<<<< HEAD
const canRetryLastTask = computed(() => status.value === "failed" && Boolean(lastSubmittedMessage.value));

function clearProgressTimers() {
  while (progressTimers.length > 0) {
    const timer = progressTimers.pop();
    if (timer !== undefined) {
      window.clearTimeout(timer);
    }
=======
// ==================== 会话管理 ====================

/**
 * 开始新对话
 * 重置所有状态，创建新的空会话
 */
function startNewSession() {
  submitting.value = false;
  uploadingDocument.value = false;
  checkingSession.value = false;
  loadingHistory.value = false;
  activeSessionId.value = "";
  activeSessionTitle.value = "新对话";
  draft.value = "";
  sessionError.value = "";
  documents.value = [];
  messages.value = createWelcomeMessages();
  resetFeedback();
  closeSidebar();
  void scrollToBottom();
}

/**
 * 应用模板（填充输入框）
 */
function applyTemplate(prompt: string) {
  draft.value = prompt;
  resetFeedback();
}

/** 处理模板选择 */
function handleTemplateSelect() {
  const template = presetTemplates.find((item) => item.label === selectedTemplate.value);
  if (!template) {
    return;
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
  }
}

<<<<<<< HEAD
function updateProgress(statusValue: TaskStatus, label: string) {
  status.value = statusValue;
  currentStatusLabel.value = label;
}

function startPendingProgress() {
  composerError.value = "";
  planSteps.value = [];
  updateProgress("submitted", stageLabelMap.submitted);

  progressTimers.push(
    window.setTimeout(() => {
      if (submitting.value) {
        updateProgress("analyzing", stageLabelMap.analyzing);
      }
    }, 250),
  );

  progressTimers.push(
    window.setTimeout(() => {
      if (submitting.value) {
        updateProgress("executing", stageLabelMap.executing);
      }
    }, 900),
  );
}

function applyCompletedTimeline(response: ChatResponse) {
  status.value = response.status;
  currentStatusLabel.value = stageLabelMap[response.status];
  planSteps.value = Array.from(new Set([...response.timeline.map((item: TaskStage) => item.label), ...response.steps]));
=======
/**
 * 触发文件下载
 */
function triggerDownload(fileName: string, content: string) {
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
}

/** 退出登录 */
function logout() {
  clearProgressTimers();
  authStore.clearSession();
  router.push("/login");
}

<<<<<<< HEAD
=======
/**
 * 处理认证错误
 * 如果是 token 失效，跳转到登录页
 * @returns 是否已处理（跳转了登录页）
 */
async function handleAuthError(error: unknown) {
  const messageText = error instanceof Error ? error.message : "请求失败";
  if (["Missing token", "Invalid token", "User not found"].includes(messageText)) {
    authStore.clearSession();
    await router.replace("/login");
    return true;
  }
  return false;
}

/**
 * 从任务记录列表还原消息列表
 * 用于加载历史会话
 */
function hydrateMessagesFromTasks(tasks: TaskRecord[]) {
  if (tasks.length === 0) {
    messages.value = createWelcomeMessages();
    return;
  }

  const nextMessages: MessageItem[] = [];
  for (const task of tasks) {
    // 用户消息
    nextMessages.push({
      id: `user-${task.id}`,
      role: "user",
      kind: "text",
      content: task.message,
    });
    // 轨迹消息
    nextMessages.push(createTraceFromTask(task));

    // 错误消息或结果
    if (task.errorMessage) {
      nextMessages.push({
        id: `assistant-error-${task.id}`,
        role: "assistant",
        kind: "error",
        prompt: task.message,
        errorMessage: task.errorMessage,
        errorHint: "这是历史执行记录中的失败结果。",
      });
      continue;
    }

    nextMessages.push({
      id: `assistant-result-${task.id}`,
      role: "assistant",
      kind: "result",
      recordId: task.id,
      intent: task.intent,
      prompt: task.message,
      result: task.result,
      sources: task.retrievedChunks,
    });
  }

  messages.value = nextMessages;
  void scrollToBottom();
}

// ==================== 数据加载 ====================

/** 加载会话列表 */
async function loadSessionList() {
  if (!authStore.token) {
    return;
  }

  loadingSessions.value = true;
  sessionError.value = "";

  try {
    const response = await fetchSessions(authStore.token);
    sessions.value = response.sessions;
  } catch (error) {
    if (await handleAuthError(error)) {
      return;
    }
    sessionError.value = error instanceof Error ? error.message : "会话列表加载失败";
  } finally {
    loadingSessions.value = false;
  }
}

/** 加载错题列表 */
async function loadMistakes() {
  if (!authStore.token) {
    return;
  }
  try {
    const response = await fetchMistakes(authStore.token);
    mistakes.value = response.items;
  } catch {
    mistakes.value = [];
  }
}

/**
 * 打开指定会话
 * 加载会话详情、历史消息和关联文档
 */
async function openSession(sessionId: string) {
  if (!authStore.token || !sessionId) {
    return;
  }

  loadingHistory.value = true;
  sessionError.value = "";

  try {
    const detail = await fetchSessionDetail(sessionId, authStore.token);
    activeSessionId.value = detail.sessionId;
    activeSessionTitle.value = detail.title;
    documents.value = detail.documents;
    hydrateMessagesFromTasks(detail.tasks);
    closeSidebar();
  } catch (error) {
    if (await handleAuthError(error)) {
      return;
    }
    sessionError.value = error instanceof Error ? error.message : "会话内容加载失败";
  } finally {
    loadingHistory.value = false;
  }
}

/**
 * 校验会话并初始化
 * 页面加载时调用，验证 token 有效性并加载初始数据
 */
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
async function validateSession() {
  if (!authStore.token) {
    checkingSession.value = false;
    router.replace("/login");
    return;
  }

  try {
    // 验证 token 获取用户信息
    const user = await fetchMe(authStore.token);
    authStore.setUser(user);
<<<<<<< HEAD
=======
    // 并行加载会话列表和错题列表
    await Promise.all([loadSessionList(), loadMistakes()]);
    // 如果有会话，打开第一个
    if (sessions.value.length > 0) {
      await openSession(sessions.value[0].sessionId);
    } else {
      startNewSession();
    }
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
  } catch {
    authStore.clearSession();
    router.replace("/login");
  } finally {
    checkingSession.value = false;
  }
}

<<<<<<< HEAD
function applyTemplate(prompt: string) {
  draft.value = prompt;
  composerError.value = "";
}

=======
// ==================== 重试功能 ====================

/** 重新回答上一条消息 */
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
function retryLastTask() {
  if (!lastSubmittedMessage.value || submitting.value) {
    return;
  }

  draft.value = lastSubmittedMessage.value;
  handleSubmit();
}

<<<<<<< HEAD
async function handleSubmit() {
  const message = draft.value.trim();
  if (submitting.value || checkingSession.value) {
    return;
  }

  if (!message) {
    composerError.value = "请输入至少 2 个字符的教育任务描述。";
    return;
  }

  if (message.length < 2) {
    composerError.value = "任务内容过短，请补充更完整的描述。";
    return;
  }

=======
/** 重新回答指定消息 */
function retryMessage(message: MessageItem) {
  if (!message.prompt || submitting.value) {
    return;
  }
  draft.value = message.prompt;
  void handleSubmit();
}

// ==================== 复制功能 ====================

/**
 * 构建复制文本
 * 将结果消息转换为纯文本格式
 */
function buildCopyText(message: MessageItem) {
  if (message.kind !== "result" || !message.result) {
    return "";
  }

  const parts: string[] = [];
  
  if (message.result.answer) {
    parts.push(message.result.answer);
  }
  if (message.result.summary) {
    parts.push(message.result.summary);
  }
  if (message.result.quiz?.length) {
    parts.push(
      [
        "练习题",
        ...message.result.quiz.map((item, index) => {
          const options = item.options.map((option, optionIndex) => `${String.fromCharCode(65 + optionIndex)}. ${option}`);
          return `${index + 1}. ${item.question}\n${options.join("\n")}\n答案：${item.answer}`;
        }),
      ].join("\n\n"),
    );
  }
  if (message.sources?.length) {
    parts.push(["资料来源", ...message.sources.map((item) => `${item.fileName}\n${item.content}`)].join("\n\n"));
  }

  return parts.join("\n\n");
}

/** 复制结果到剪贴板 */
async function handleCopy(message: MessageItem) {
  const text = buildCopyText(message);
  if (!text) {
    composerError.value = "当前结果没有可复制的内容";
    composerNotice.value = "";
    return;
  }

  try {
    await navigator.clipboard.writeText(text);
    composerNotice.value = "回答内容已复制到剪贴板";
    composerError.value = "";
  } catch {
    composerError.value = "复制失败，请检查浏览器剪贴板权限";
    composerNotice.value = "";
  }
}

// ==================== 文件上传 ====================

/**
 * 处理文件选择
 * 上传文档到服务器
 */
async function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  // 清空 input，允许重复选择同一文件
  target.value = "";

  if (!file || !authStore.token) {
    return;
  }

  uploadingDocument.value = true;
  resetFeedback();
  composerNotice.value = `正在上传：${file.name}`;

  try {
    // 上传文档
    const uploaded = await uploadDocument(file, authStore.token, activeSessionId.value || undefined);
    // 更新当前会话 ID（新建会话时会返回新的 sessionId）
    activeSessionId.value = uploaded.sessionId;
    // 更新文档列表（避免重复）
    documents.value = [...documents.value.filter((item) => item.documentId !== uploaded.documentId), uploaded];
    composerNotice.value = `资料已上传：${uploaded.fileName}`;
    // 刷新会话列表
    await loadSessionList();
    // 更新会话标题
    const currentSession = sessions.value.find((item) => item.sessionId === uploaded.sessionId);
    activeSessionTitle.value = currentSession?.title ?? activeSessionTitle.value;
  } catch (error) {
    if (await handleAuthError(error)) {
      return;
    }
    composerError.value = error instanceof Error ? error.message : "资料上传失败";
    composerNotice.value = "";
  } finally {
    uploadingDocument.value = false;
  }
}

// ==================== 导出功能 ====================

/** 导出任务结果为 Markdown */
async function handleExport(recordId?: number) {
  if (!recordId || !authStore.token) {
    return;
  }

  try {
    const exported = await exportTaskResult(recordId, authStore.token);
    triggerDownload(exported.fileName, exported.content);
    composerNotice.value = "结果已导出";
    composerError.value = "";
  } catch (error) {
    composerError.value = error instanceof Error ? error.message : "导出失败";
    composerNotice.value = "";
  }
}

// ==================== 答题功能 ====================

/**
 * 提交答题答案
 * 调用后端 API 获取反馈，并更新错题列表
 */
async function handleQuizSubmit(recordId: number | undefined, answers: Array<{ questionIndex: number; userAnswer: string }>) {
  if (!recordId || !authStore.token) {
    return;
  }

  try {
    const response = await submitQuizAttempt(recordId, answers, authStore.token);
    // 更新消息的答题反馈
    const target = messages.value.find((item) => item.recordId === recordId);
    if (target) {
      target.quizFeedback = response.message;
    }
    // 刷新错题列表
    await loadMistakes();
  } catch (error) {
    const target = messages.value.find((item) => item.recordId === recordId);
    if (target) {
      target.quizFeedback = error instanceof Error ? error.message : "提交作答失败";
    }
  }
}

// ==================== 发送消息 ====================

/**
 * 发送消息的核心函数
 * 1. 创建待处理轨迹
 * 2. 调用 executeTask API
 * 3. 更新轨迹和结果消息
 * 4. 处理错误
 */
async function sendMessage(message: string) {
  // 创建待处理轨迹消息
  const pendingTrace = createPendingTrace(message);

  // 添加用户消息
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
  messages.value.push({
    id: crypto.randomUUID(),
    role: "user",
    kind: "text",
    content: message,
  });
<<<<<<< HEAD

=======
  // 添加轨迹消息
  messages.value.push(pendingTrace);

  // 清空输入框，设置提交状态
  draft.value = "";
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
  submitting.value = true;
  composerError.value = "";
  intent.value = "";
  lastSubmittedMessage.value = message;
  startPendingProgress();

  try {
<<<<<<< HEAD
    const response = await executeTask(message, authStore.token);
    clearProgressTimers();
    intent.value = response.intent;
    applyCompletedTimeline(response);
=======
    // 调用 API 执行任务
    const response = await executeTask(message, authStore.token, activeSessionId.value || undefined);
    
    // 更新当前会话 ID（新建会话时）
    activeSessionId.value = response.sessionId;
    
    // 更新关联的文档列表
    if (response.usedDocuments.length > 0) {
      documents.value = response.usedDocuments;
    }

    // 替换待处理轨迹为实际响应
    replaceMessage(pendingTrace.id, createTraceFromResponse(response, message));
    
    // 添加结果消息
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
    messages.value.push({
      id: response.taskId,
      role: "assistant",
      kind: "result",
      intent: response.intent,
      result: response.result,
    });
<<<<<<< HEAD
    draft.value = "";
  } catch (error) {
    clearProgressTimers();
=======

    // 刷新会话列表
    await loadSessionList();
    // 更新会话标题
    const currentSession = sessions.value.find((item) => item.sessionId === response.sessionId);
    activeSessionTitle.value = currentSession?.title ?? activeSessionTitle.value;
    await scrollToBottom();
  } catch (error) {
    if (await handleAuthError(error)) {
      return;
    }
    // 创建失败的轨迹和错误消息
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
    const messageText = error instanceof Error ? error.message : "请求失败";
    const sessionExpired = ["Missing token", "Invalid token", "User not found"].includes(messageText);
    status.value = "failed";
    currentStatusLabel.value = stageLabelMap.failed;
    planSteps.value = [
      stageLabelMap.submitted,
      stageLabelMap.analyzing,
      sessionExpired ? "登录状态失效，需要重新认证" : "任务执行中断，请检查输入或稍后重试",
    ];
    composerError.value = sessionExpired ? "登录已失效，请重新登录后再发送任务。" : "任务执行失败，可直接重试上一次任务。";
    messages.value.push({
      id: crypto.randomUUID(),
      role: "assistant",
      kind: "error",
      errorMessage: messageText,
<<<<<<< HEAD
      errorHint: sessionExpired ? "请重新登录后再次提交任务。" : "可以点击“重试上次任务”，或修改描述后重新发送。",
=======
      errorHint: "可以点击「重新回答」，或者修改问题后再次发送。",
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
    });
    if (sessionExpired) {
      authStore.clearSession();
      window.setTimeout(() => {
        router.replace("/login");
      }, 600);
    }
  } finally {
    submitting.value = false;
  }
}

<<<<<<< HEAD
onMounted(() => {
  validateSession();
  
  // Check if user just logged in, show success toast
  if (sessionStorage.getItem('loginSuccess') === 'true') {
    sessionStorage.removeItem('loginSuccess');
    toastMessage.value = `欢迎回来，${authStore.username || '用户'}！`;
    toastType.value = "success";
    toastVisible.value = true;
  }
=======
/**
 * 处理表单提交
 * 验证输入后调用 sendMessage
 */
async function handleSubmit() {
  // 防重复提交
  if (submitting.value || checkingSession.value || loadingHistory.value) {
    return;
  }

  const message = draft.value.trim();
  // 简单验证
  if (!message || message.length < 2) {
    composerError.value = "请输入至少 2 个字符的学习问题或任务描述。";
    composerNotice.value = "";
    return;
  }

  await sendMessage(message);
}

// ==================== 响应式处理 ====================

/** 处理窗口大小变化 */
function handleResize() {
  // 大屏自动打开侧边栏
  if (window.innerWidth > 1080) {
    isSidebarOpen.value = true;
  }
}

// ==================== 生命周期 ====================

onMounted(() => {
  // 监听窗口大小变化
  window.addEventListener("resize", handleResize);
  // 初始化会话
  void validateSession();
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
});

onBeforeUnmount(() => {
  clearProgressTimers();
});
</script>
