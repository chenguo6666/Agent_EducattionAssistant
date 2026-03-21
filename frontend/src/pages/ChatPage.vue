<template>
  <main class="chat-layout chatgpt-shell" :class="{ 'sidebar-open': isSidebarOpen }">
    <button v-if="!isSidebarOpen" class="sidebar-toggle floating-toggle" type="button" @click="toggleSidebar">
      菜单
    </button>
    <div v-if="isSidebarOpen" class="sidebar-backdrop" @click="closeSidebar"></div>

    <aside class="sidebar-card chatgpt-sidebar" :class="{ open: isSidebarOpen }">
      <div class="sidebar-top">
        <div class="sidebar-toolbar">
          <button class="secondary-button sidebar-new-chat" type="button" @click="startNewSession">+ 新建对话</button>
          <button class="icon-action-button sidebar-close" type="button" @click="closeSidebar">收起</button>
        </div>

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

      <div class="sidebar-bottom">
        <div class="sidebar-meta">
          <span class="status-label">当前用户</span>
          <strong>{{ authStore.username || "未登录用户" }}</strong>
        </div>
        <div class="sidebar-meta">
          <span class="status-label">当前会话</span>
          <strong>{{ activeSessionTitle }}</strong>
        </div>
        <button class="secondary-button sidebar-logout" type="button" @click="logout">退出登录</button>
      </div>
    </aside>

    <section class="chat-card chatgpt-main">
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

      <div ref="messageListRef" class="message-list chatgpt-message-list">
        <div v-if="loadingHistory" class="chat-area-empty">正在加载对话内容...</div>
        <template v-else v-for="message in messages" :key="message.id">
          <MessageBubble v-if="message.kind === 'text'" :role="message.role" :content="message.content ?? ''" />

          <AgentTraceCard
            v-else-if="message.kind === 'trace'"
            :intent="message.intent"
            :status="message.status"
            :timeline="message.timeline"
            :agent-trace="message.agentTrace"
            :tool-calls="message.toolCalls"
            :loading="message.loading"
          />

          <TaskResultCard
            v-else-if="message.kind === 'result'"
            :intent="message.intent ?? 'unknown'"
            :result="message.result!"
            :sources="message.sources ?? []"
            :quiz-feedback="message.quizFeedback"
            @copy="handleCopy(message)"
            @export="handleExport(message.recordId)"
            @retry="retryMessage(message)"
            @submit-quiz="handleQuizSubmit(message.recordId, $event)"
          />

          <TaskErrorCard
            v-else
            :message="message.errorMessage ?? '请求失败'"
            :hint="message.errorHint ?? '请检查输入后重试。'"
          />
        </template>
      </div>

      <div class="chatgpt-composer-wrap">
        <form class="chat-form chatgpt-form compact-composer" @submit.prevent="handleSubmit">
          <p v-if="composerNotice" class="inline-feedback success">{{ composerNotice }}</p>
          <p v-if="composerError" class="inline-feedback">{{ composerError }}</p>

          <div class="composer-controls">
            <div class="composer-toolbar">
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
              <select v-model="selectedTemplate" class="template-select" @change="handleTemplateSelect">
                <option value="">快捷任务</option>
                <option v-for="template in presetTemplates" :key="template.label" :value="template.label">
                  {{ template.label }}
                </option>
              </select>
            </div>

            <div v-if="documents.length > 0" class="composer-document-row">
              <span class="composer-document-label">资料</span>
              <div class="composer-document-list">
                <span v-for="document in documents" :key="document.documentId" class="composer-document-chip">
                  {{ document.fileName }}
                </span>
              </div>
            </div>
          </div>

          <textarea
            v-model="draft"
            rows="1"
            placeholder="有问题，尽管问"
            :disabled="submitting || checkingSession || loadingHistory"
          />

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
          </div>
        </form>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { fetchMe } from "@/api/auth";
import {
  executeTask,
  exportTaskResult,
  fetchMistakes,
  fetchSessionDetail,
  fetchSessions,
  submitQuizAttempt,
} from "@/api/chat";
import { uploadDocument } from "@/api/documents";
import AgentTraceCard from "@/components/AgentTraceCard.vue";
import MessageBubble from "@/components/MessageBubble.vue";
import TaskErrorCard from "@/components/TaskErrorCard.vue";
import TaskResultCard from "@/components/TaskResultCard.vue";
import { useAuthStore } from "@/stores/auth";
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

type MessageKind = "text" | "trace" | "result" | "error";

interface MessageItem {
  id: string;
  role: "user" | "assistant";
  kind: MessageKind;
  recordId?: number;
  content?: string;
  prompt?: string;
  result?: ChatResult;
  sources?: RetrievedChunk[];
  quizFeedback?: string;
  intent?: string;
  status?: TaskStatus | "thinking";
  timeline?: TaskStage[];
  agentTrace?: AgentTraceItem[];
  toolCalls?: ToolCallItem[];
  loading?: boolean;
  errorMessage?: string;
  errorHint?: string;
}

const router = useRouter();
const authStore = useAuthStore();
const messageListRef = ref<HTMLElement | null>(null);

const isSidebarOpen = ref(window.innerWidth > 1080);
const draft = ref("");
const selectedTemplate = ref("");
const submitting = ref(false);
const uploadingDocument = ref(false);
const checkingSession = ref(true);
const loadingSessions = ref(false);
const loadingHistory = ref(false);
const composerError = ref("");
const composerNotice = ref("");
const lastSubmittedMessage = ref("");
const sessionError = ref("");
const sessions = ref<ChatSessionSummary[]>([]);
const documents = ref<DocumentSummary[]>([]);
const mistakes = ref<MistakeItem[]>([]);
const activeSessionId = ref("");
const activeSessionTitle = ref("新对话");
const messages = ref<MessageItem[]>(createWelcomeMessages());

const presetTemplates = [
  {
    label: "自由聊天",
    prompt: "请先根据我的情况给我一些学习建议：",
  },
  {
    label: "总结 + 出题",
    prompt: "请根据当前资料总结重点，并生成 5 个选择题帮助我复习。",
  },
  {
    label: "资料追问",
    prompt: "请根据当前资料回答：",
  },
  {
    label: "知识点提取",
    prompt: "请提取这份资料的核心知识点。",
  },
  {
    label: "复习提纲",
    prompt: "请生成这份资料的复习提纲。",
  },
];

const canRetryLastTask = computed(() => Boolean(lastSubmittedMessage.value) && !submitting.value);

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

function createPendingTrace(prompt: string): MessageItem {
  return {
    id: `trace-${crypto.randomUUID()}`,
    role: "assistant",
    kind: "trace",
    prompt,
    status: "thinking",
    loading: true,
    timeline: [
      { status: "submitted", label: "任务已提交" },
      { status: "analyzing", label: "分析中" },
      { status: "executing", label: "执行中" },
    ],
    agentTrace: [],
    toolCalls: [],
  };
}

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

function replaceMessage(messageId: string, nextMessage: MessageItem) {
  const index = messages.value.findIndex((item) => item.id === messageId);
  if (index === -1) {
    messages.value.push(nextMessage);
    return;
  }
  messages.value.splice(index, 1, nextMessage);
}

function resetFeedback() {
  composerError.value = "";
  composerNotice.value = "";
}

function toggleSidebar() {
  isSidebarOpen.value = !isSidebarOpen.value;
}

function closeSidebar() {
  isSidebarOpen.value = false;
}

async function scrollToBottom() {
  await nextTick();
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight;
  }
}

function formatSessionTime(value: string) {
  return new Date(value).toLocaleString("zh-CN", {
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

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

function applyTemplate(prompt: string) {
  draft.value = prompt;
  resetFeedback();
}

function handleTemplateSelect() {
  const template = presetTemplates.find((item) => item.label === selectedTemplate.value);
  if (!template) {
    return;
  }
  applyTemplate(template.prompt);
  selectedTemplate.value = "";
}

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
}

function logout() {
  authStore.clearSession();
  router.push("/login");
}

async function handleAuthError(error: unknown) {
  const messageText = error instanceof Error ? error.message : "请求失败";
  if (["Missing token", "Invalid token", "User not found"].includes(messageText)) {
    authStore.clearSession();
    await router.replace("/login");
    return true;
  }
  return false;
}

function hydrateMessagesFromTasks(tasks: TaskRecord[]) {
  if (tasks.length === 0) {
    messages.value = createWelcomeMessages();
    return;
  }

  const nextMessages: MessageItem[] = [];
  for (const task of tasks) {
    nextMessages.push({
      id: `user-${task.id}`,
      role: "user",
      kind: "text",
      content: task.message,
    });
    nextMessages.push(createTraceFromTask(task));

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

async function validateSession() {
  if (!authStore.token) {
    checkingSession.value = false;
    await router.replace("/login");
    return;
  }

  try {
    const user = await fetchMe(authStore.token);
    authStore.setUser(user);
    await Promise.all([loadSessionList(), loadMistakes()]);
    if (sessions.value.length > 0) {
      await openSession(sessions.value[0].sessionId);
    } else {
      startNewSession();
    }
  } catch {
    authStore.clearSession();
    await router.replace("/login");
  } finally {
    checkingSession.value = false;
  }
}

function retryLastTask() {
  if (!lastSubmittedMessage.value || submitting.value) {
    return;
  }
  draft.value = lastSubmittedMessage.value;
  void handleSubmit();
}

function retryMessage(message: MessageItem) {
  if (!message.prompt || submitting.value) {
    return;
  }
  draft.value = message.prompt;
  void handleSubmit();
}

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

async function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  target.value = "";

  if (!file || !authStore.token) {
    return;
  }

  uploadingDocument.value = true;
  resetFeedback();
  composerNotice.value = `正在上传：${file.name}`;

  try {
    const uploaded = await uploadDocument(file, authStore.token, activeSessionId.value || undefined);
    activeSessionId.value = uploaded.sessionId;
    documents.value = [...documents.value.filter((item) => item.documentId !== uploaded.documentId), uploaded];
    composerNotice.value = `资料已上传：${uploaded.fileName}`;
    await loadSessionList();
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

async function handleQuizSubmit(recordId: number | undefined, answers: Array<{ questionIndex: number; userAnswer: string }>) {
  if (!recordId || !authStore.token) {
    return;
  }

  try {
    const response = await submitQuizAttempt(recordId, answers, authStore.token);
    const target = messages.value.find((item) => item.recordId === recordId);
    if (target) {
      target.quizFeedback = response.message;
    }
    await loadMistakes();
  } catch (error) {
    const target = messages.value.find((item) => item.recordId === recordId);
    if (target) {
      target.quizFeedback = error instanceof Error ? error.message : "提交作答失败";
    }
  }
}

async function sendMessage(message: string) {
  const pendingTrace = createPendingTrace(message);

  messages.value.push({
    id: `user-${crypto.randomUUID()}`,
    role: "user",
    kind: "text",
    content: message,
  });
  messages.value.push(pendingTrace);

  draft.value = "";
  submitting.value = true;
  resetFeedback();
  lastSubmittedMessage.value = message;
  closeSidebar();
  await scrollToBottom();

  try {
    const response = await executeTask(message, authStore.token, activeSessionId.value || undefined);
    activeSessionId.value = response.sessionId;
    if (response.usedDocuments.length > 0) {
      documents.value = response.usedDocuments;
    }

    replaceMessage(pendingTrace.id, createTraceFromResponse(response, message));
    messages.value.push({
      id: response.taskId,
      role: "assistant",
      kind: "result",
      recordId: response.recordId,
      intent: response.intent,
      prompt: message,
      result: response.result,
      sources: response.retrievedChunks,
    });

    await loadSessionList();
    const currentSession = sessions.value.find((item) => item.sessionId === response.sessionId);
    activeSessionTitle.value = currentSession?.title ?? activeSessionTitle.value;
    await scrollToBottom();
  } catch (error) {
    if (await handleAuthError(error)) {
      return;
    }
    const messageText = error instanceof Error ? error.message : "请求失败";
    replaceMessage(pendingTrace.id, createFailedTrace(message, messageText));
    messages.value.push({
      id: `error-${crypto.randomUUID()}`,
      role: "assistant",
      kind: "error",
      prompt: message,
      errorMessage: messageText,
      errorHint: "可以点击“重新回答”，或者修改问题后再次发送。",
    });
    composerError.value = "任务执行失败，可以直接重新回答上一条消息。";
    composerNotice.value = "";
    await scrollToBottom();
  } finally {
    submitting.value = false;
  }
}

async function handleSubmit() {
  if (submitting.value || checkingSession.value || loadingHistory.value) {
    return;
  }

  const message = draft.value.trim();
  if (!message || message.length < 2) {
    composerError.value = "请输入至少 2 个字符的学习问题或任务描述。";
    composerNotice.value = "";
    return;
  }

  await sendMessage(message);
}

function handleResize() {
  if (window.innerWidth > 1080) {
    isSidebarOpen.value = true;
  }
}

onMounted(() => {
  window.addEventListener("resize", handleResize);
  void validateSession();
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize);
});
</script>
