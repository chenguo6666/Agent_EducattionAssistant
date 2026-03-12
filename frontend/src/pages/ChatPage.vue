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

        <details class="sidebar-disclosure">
          <summary>Agent 面板</summary>
          <div class="sidebar-disclosure-content">
            <div class="agent-strip-group">
              <span class="status-label">执行阶段</span>
              <div class="agent-strip-pills">
                <span
                  v-for="stage in stageCards"
                  :key="stage.status"
                  class="stage-pill"
                  :class="stage.stateClass"
                >
                  {{ stage.title }} · {{ stage.stateLabel }}
                </span>
              </div>
            </div>
            <div class="agent-strip-group">
              <span class="status-label">执行计划</span>
              <div class="plan-inline">
                <span v-for="step in planSteps" :key="step" class="plan-inline-item">{{ step }}</span>
                <span v-if="planSteps.length === 0" class="plan-inline-item muted">等待任务分析</span>
              </div>
            </div>
          </div>
        </details>

        <section class="sidebar-section">
          <div class="session-panel-header">
            <p class="sidebar-section-title">最近错题</p>
            <span class="muted">{{ mistakes.length }} 条</span>
          </div>
          <div v-if="mistakes.length === 0" class="session-empty">提交选择题作答后，答错的题会记录在这里。</div>
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
          <strong>{{ authStore.username || "未命名用户" }}</strong>
        </div>
        <div class="sidebar-meta">
          <span class="status-label">当前会话</span>
          <strong>{{ activeSessionTitle }}</strong>
        </div>
        <div class="sidebar-meta">
          <span class="status-label">任务状态</span>
          <strong>{{ currentStatusLabel }}</strong>
        </div>
        <div class="sidebar-meta">
          <span class="status-label">识别意图</span>
          <strong>{{ intent || "等待提交" }}</strong>
        </div>
        <button class="secondary-button sidebar-logout" type="button" @click="logout">退出登录</button>
      </div>
    </aside>

    <section class="chat-card chatgpt-main">
      <header class="chatgpt-header compact-topbar">
        <div class="topbar-title">
          <button class="icon-action-button sidebar-toggle-inline" type="button" @click="toggleSidebar">菜单</button>
          <strong>Education Assistant</strong>
          <span class="muted">教育助手 AI Agent</span>
        </div>
        <div class="header-badges">
          <span class="stage-pill">{{ documents.length > 0 ? "资料模式" : "自由聊天" }}</span>
          <span class="stage-pill">{{ intent || "等待指令" }}</span>
        </div>
      </header>

      <div ref="messageListRef" class="message-list chatgpt-message-list">
        <div v-if="loadingHistory" class="chat-area-empty">正在加载对话内容...</div>
        <template v-else v-for="message in messages" :key="message.id">
          <MessageBubble v-if="message.kind === 'text'" :role="message.role" :content="message.content ?? ''" />
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

          <textarea v-model="draft" rows="1" placeholder="有问题，尽管问" />

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
import MessageBubble from "@/components/MessageBubble.vue";
import TaskErrorCard from "@/components/TaskErrorCard.vue";
import TaskResultCard from "@/components/TaskResultCard.vue";
import { useAuthStore } from "@/stores/auth";
import type {
  ChatResponse,
  ChatResult,
  ChatSessionSummary,
  DocumentSummary,
  MistakeItem,
  RetrievedChunk,
  TaskRecord,
  TaskStage,
  TaskStatus,
} from "@/types/chat";

type MessageKind = "text" | "result" | "error";

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
  errorMessage?: string;
  errorHint?: string;
}

const router = useRouter();
const authStore = useAuthStore();
const messageListRef = ref<HTMLElement | null>(null);

const defaultDraft = "";
const isSidebarOpen = ref(window.innerWidth > 1080);

const draft = ref(defaultDraft);
const selectedTemplate = ref("");
const submitting = ref(false);
const uploadingDocument = ref(false);
const checkingSession = ref(true);
const loadingSessions = ref(false);
const loadingHistory = ref(false);
const status = ref<TaskStatus | "idle">("idle");
const intent = ref("");
const planSteps = ref<string[]>([]);
const currentStatusLabel = ref("等待提交");
const progressTimers: number[] = [];
const composerError = ref("");
const composerNotice = ref("");
const lastSubmittedMessage = ref("");
const sessionError = ref("");
const documentFeedback = ref("");
const documentFeedbackType = ref<"error" | "success">("success");
const sessions = ref<ChatSessionSummary[]>([]);
const documents = ref<DocumentSummary[]>([]);
const mistakes = ref<MistakeItem[]>([]);
const activeSessionId = ref("");
const activeSessionTitle = ref("新对话");
const messages = ref<MessageItem[]>(createWelcomeMessages());

const presetTemplates = [
  {
    label: "自由聊天",
    description: "不上传资料，直接提学习问题",
    prompt: "请先根据我的情况给我一些学习建议：",
  },
  {
    label: "总结 + 出题",
    description: "适合上传资料后的复习场景",
    prompt: "请根据当前资料总结重点，并生成 5 个选择题帮助我复习。",
  },
  {
    label: "资料追问",
    description: "围绕当前资料继续发问",
    prompt: "请根据当前资料回答：",
  },
];

const stageLabelMap: Record<TaskStatus, string> = {
  submitted: "任务已提交",
  analyzing: "分析中",
  executing: "执行中",
  completed: "已完成",
  failed: "执行失败",
};

const orderedStages: TaskStatus[] = ["submitted", "analyzing", "executing", "completed"];
const stageTitleMap: Record<TaskStatus, string> = {
  submitted: "提交",
  analyzing: "分析",
  executing: "执行",
  completed: "完成",
  failed: "失败",
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
      stateClass,
      stateLabel,
    };
  });
});

const canRetryLastTask = computed(() => Boolean(lastSubmittedMessage.value) && !submitting.value);

function createWelcomeMessages(): MessageItem[] {
  return [
    {
      id: "welcome",
      role: "assistant",
      kind: "text",
      content:
        "你好，我可以直接作为学习助手和你对话，也可以在上传资料后帮你总结、出题和进行资料追问。你可以直接开始提问。",
    },
  ];
}

function clearProgressTimers() {
  while (progressTimers.length > 0) {
    const timer = progressTimers.pop();
    if (timer !== undefined) {
      window.clearTimeout(timer);
    }
  }
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

function updateProgress(statusValue: TaskStatus, label: string) {
  status.value = statusValue;
  currentStatusLabel.value = label;
}

function resetInspectorState() {
  status.value = "idle";
  currentStatusLabel.value = "等待提交";
  intent.value = "";
  planSteps.value = [];
}

function resetDocumentFeedback() {
  documentFeedback.value = "";
  documentFeedbackType.value = "success";
}

function startPendingProgress() {
  resetFeedback();
  planSteps.value = [];
  updateProgress("submitted", stageLabelMap.submitted);

  progressTimers.push(
    window.setTimeout(() => {
      if (submitting.value) {
        updateProgress("analyzing", stageLabelMap.analyzing);
      }
    }, 200),
  );

  progressTimers.push(
    window.setTimeout(() => {
      if (submitting.value) {
        updateProgress("executing", stageLabelMap.executing);
      }
    }, 800),
  );
}

function applyCompletedTimeline(response: ChatResponse) {
  status.value = response.status;
  currentStatusLabel.value = stageLabelMap[response.status];
  planSteps.value = Array.from(new Set([...response.timeline.map((item: TaskStage) => item.label), ...response.steps]));
}

function applyTaskRecordState(record: TaskRecord) {
  status.value = record.status;
  currentStatusLabel.value = stageLabelMap[record.status];
  intent.value = record.intent;
  planSteps.value = Array.from(new Set([...record.timeline.map((item: TaskStage) => item.label), ...record.steps]));
}

function hydrateMessagesFromTasks(tasks: TaskRecord[]) {
  if (tasks.length === 0) {
    messages.value = createWelcomeMessages();
    resetInspectorState();
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

    if (task.errorMessage) {
      nextMessages.push({
        id: `assistant-error-${task.id}`,
        role: "assistant",
        kind: "error",
        prompt: task.message,
        errorMessage: task.errorMessage,
        errorHint: "这是历史执行记录中的失败结果。",
      });
    } else {
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
  }

  messages.value = nextMessages;
  applyTaskRecordState(tasks[tasks.length - 1]);
  void scrollToBottom();
}

function formatSessionTime(value: string) {
  return new Date(value).toLocaleString("zh-CN", {
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

async function scrollToBottom() {
  await nextTick();
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight;
  }
}

function startNewSession() {
  clearProgressTimers();
  activeSessionId.value = "";
  activeSessionTitle.value = "新对话";
  draft.value = defaultDraft;
  sessionError.value = "";
  documents.value = [];
  messages.value = createWelcomeMessages();
  resetInspectorState();
  resetFeedback();
  resetDocumentFeedback();
  closeSidebar();
  void scrollToBottom();
}

function applyTemplate(prompt: string) {
  draft.value = prompt;
  resetFeedback();
  closeSidebar();
}

function handleTemplateSelect() {
  const matchedTemplate = presetTemplates.find((template) => template.label === selectedTemplate.value);
  if (!matchedTemplate) {
    return;
  }
  applyTemplate(matchedTemplate.prompt);
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
  clearProgressTimers();
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
  resetDocumentFeedback();

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
    router.replace("/login");
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
    router.replace("/login");
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
    parts.push(`回答内容\n${message.result.answer}`);
  }
  if (message.result.summary) {
    parts.push(`摘要结果\n${message.result.summary}`);
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
  resetDocumentFeedback();
  documentFeedback.value = `正在上传：${file.name}`;
  documentFeedbackType.value = "success";
  composerNotice.value = documentFeedback.value;

  try {
    const uploaded = await uploadDocument(file, authStore.token, activeSessionId.value || undefined);
    activeSessionId.value = uploaded.sessionId;
    documents.value = [...documents.value.filter((item) => item.documentId !== uploaded.documentId), uploaded];
    documentFeedback.value = `资料已上传：${uploaded.fileName}`;
    documentFeedbackType.value = "success";
    composerNotice.value = documentFeedback.value;
    await loadSessionList();
    const currentSession = sessions.value.find((item) => item.sessionId === uploaded.sessionId);
    activeSessionTitle.value = currentSession?.title ?? activeSessionTitle.value;
  } catch (error) {
    if (await handleAuthError(error)) {
      return;
    }
    documentFeedback.value = error instanceof Error ? error.message : "资料上传失败";
    documentFeedbackType.value = "error";
    composerError.value = documentFeedback.value;
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
  messages.value.push({
    id: crypto.randomUUID(),
    role: "user",
    kind: "text",
    content: message,
  });

  draft.value = "";
  submitting.value = true;
  resetFeedback();
  intent.value = "";
  lastSubmittedMessage.value = message;
  startPendingProgress();
  closeSidebar();
  await scrollToBottom();

  try {
    const response = await executeTask(message, authStore.token, activeSessionId.value || undefined);
    clearProgressTimers();
    activeSessionId.value = response.sessionId;
    applyCompletedTimeline(response);
    intent.value = response.intent;
    if (response.usedDocuments.length > 0) {
      documents.value = response.usedDocuments;
    }
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
    clearProgressTimers();
    if (await handleAuthError(error)) {
      return;
    }
    const messageText = error instanceof Error ? error.message : "请求失败";
    status.value = "failed";
    currentStatusLabel.value = stageLabelMap.failed;
    planSteps.value = [stageLabelMap.submitted, stageLabelMap.analyzing, "任务执行中断，请检查输入后重试"];
    composerError.value = "任务执行失败，可以直接重新回答上一条消息。";
    composerNotice.value = "";
    messages.value.push({
      id: crypto.randomUUID(),
      role: "assistant",
      kind: "error",
      prompt: message,
      errorMessage: messageText,
      errorHint: "可以点击“重新回答”，或者修改描述后重新发送。",
    });
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
  clearProgressTimers();
  window.removeEventListener("resize", handleResize);
});
</script>
