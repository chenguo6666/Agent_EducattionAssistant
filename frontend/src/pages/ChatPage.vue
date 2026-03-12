<template>
  <main class="chat-layout">
    <aside class="sidebar-card">
      <div>
        <p class="eyebrow">教育场景 Agent</p>
        <h1>对话工作台</h1>
        <p class="muted">当前阶段已支持资料上传、轻量 RAG、结果导出和错题整理。</p>
      </div>

      <div class="status-panel hero-status-panel">
        <div>
          <span class="status-label">当前用户</span>
          <strong>{{ authStore.username || "未命名用户" }}</strong>
        </div>
        <div>
          <span class="status-label">任务状态</span>
          <strong>{{ currentStatusLabel }}</strong>
        </div>
        <div>
          <span class="status-label">当前会话</span>
          <strong>{{ activeSessionTitle }}</strong>
        </div>
        <div>
          <span class="status-label">识别意图</span>
          <strong>{{ intent || "等待提交" }}</strong>
        </div>
      </div>

      <div class="session-panel">
        <div class="session-panel-header">
          <p class="status-label">历史会话</p>
          <button class="secondary-button compact-button" type="button" @click="startNewSession">新建会话</button>
        </div>
        <p v-if="sessionError" class="inline-feedback">{{ sessionError }}</p>
        <div v-if="loadingSessions" class="session-empty">会话加载中...</div>
        <div v-else-if="sessions.length === 0" class="session-empty">还没有历史会话，先发送一条任务或上传资料即可创建。</div>
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
      </div>

      <div class="document-panel">
        <div class="session-panel-header">
          <p class="status-label">会话资料</p>
          <label class="secondary-button compact-button upload-button">
            上传资料
            <input
              class="file-input"
              type="file"
              accept=".txt,.md,.pdf,.docx"
              :disabled="uploadingDocument"
              @change="handleFileChange"
            />
          </label>
        </div>
        <p class="muted">支持 txt、md、pdf、docx。上传后会自动分块、检索并作为当前会话上下文。</p>
        <p v-if="documentFeedback" class="inline-feedback" :class="{ success: documentFeedbackType === 'success' }">
          {{ documentFeedback }}
        </p>
        <div v-if="documents.length === 0" class="session-empty">当前会话还没有上传资料。</div>
        <div v-else class="document-list">
          <article v-for="document in documents" :key="document.documentId" class="document-item">
            <div class="document-item-header">
              <strong>{{ document.fileName }}</strong>
              <span class="stage-pill">{{ document.fileType.toUpperCase() }}</span>
            </div>
            <p>{{ document.snippet || "资料已上传，等待解析内容展示。" }}</p>
          </article>
        </div>
      </div>

      <div class="mistake-panel">
        <div class="session-panel-header">
          <p class="status-label">错题本</p>
          <span class="muted">最近 {{ mistakes.length }} 条</span>
        </div>
        <div v-if="mistakes.length === 0" class="session-empty">提交题目作答后，答错的题会自动记录在这里。</div>
        <div v-else class="mistake-list">
          <article v-for="mistake in mistakes" :key="mistake.id" class="mistake-item">
            <strong>{{ mistake.question }}</strong>
            <p>你的答案：{{ mistake.userAnswer }}，正确答案：{{ mistake.correctAnswer }}</p>
            <small v-if="mistake.sourceExcerpt">{{ mistake.sourceExcerpt }}</small>
          </article>
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

    <section class="chat-card">
      <div class="message-list">
        <div v-if="loadingHistory" class="session-empty">会话内容加载中...</div>
        <template v-else v-for="message in messages" :key="message.id">
          <MessageBubble v-if="message.kind === 'text'" :role="message.role" :content="message.content ?? ''" />
          <TaskResultCard
            v-else-if="message.kind === 'result'"
            :intent="message.intent ?? 'unknown'"
            :result="message.result!"
            :sources="message.sources ?? []"
            :quiz-feedback="message.quizFeedback"
            @export="handleExport(message.recordId)"
            @submit-quiz="handleQuizSubmit(message.recordId, $event)"
          />
          <TaskErrorCard
            v-else
            :message="message.errorMessage ?? '请求失败'"
            :hint="message.errorHint ?? '请检查任务描述后重试。'"
          />
        </template>
      </div>

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
          </div>
        </div>

        <div v-if="documents.length > 0" class="context-banner">
          当前会话已挂载 {{ documents.length }} 份资料，本次任务会自动进行检索并基于相关片段执行。
        </div>

        <p v-if="composerError" class="inline-feedback">{{ composerError }}</p>
        <textarea
          v-model="draft"
          rows="5"
          placeholder="例如：工业革命带来了哪些社会问题？请根据当前资料回答。"
        />
        <div class="chat-actions">
          <span class="muted">支持资料追问、摘要生成、出题和复习提纲。</span>
          <div class="chat-action-buttons">
            <button v-if="canRetryLastTask" class="secondary-button" type="button" @click="retryLastTask">
              重试上次任务
            </button>
            <button class="primary-button" type="submit" :disabled="submitting || checkingSession || loadingHistory">
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
import { executeTask, exportTaskResult, fetchMistakes, fetchSessionDetail, fetchSessions, submitQuizAttempt } from "@/api/chat";
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
  result?: ChatResult;
  sources?: RetrievedChunk[];
  quizFeedback?: string;
  intent?: string;
  errorMessage?: string;
  errorHint?: string;
}

const router = useRouter();
const authStore = useAuthStore();

const defaultDraft = "请根据当前资料总结重点，并生成 5 个选择题帮助我复习。";

const draft = ref(defaultDraft);
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
const lastSubmittedMessage = ref("");
const sessionError = ref("");
const documentFeedback = ref("");
const documentFeedbackType = ref<"error" | "success">("success");
const sessions = ref<ChatSessionSummary[]>([]);
const documents = ref<DocumentSummary[]>([]);
const mistakes = ref<MistakeItem[]>([]);
const activeSessionId = ref("");
const activeSessionTitle = ref("新会话");
const messages = ref<MessageItem[]>(createWelcomeMessages());

const presetTemplates = [
  {
    label: "总结 + 出题",
    description: "适合历史、语文、政治类材料",
    prompt: "请根据当前资料总结重点，并生成 5 个选择题帮助我复习。",
  },
  {
    label: "提取知识点",
    description: "把资料压缩成复习要点",
    prompt: "请根据当前资料提取核心知识点，并按条目列出。",
  },
  {
    label: "资料追问",
    description: "根据当前资料回答具体问题",
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
  submitted: "任务提交",
  analyzing: "意图分析",
  executing: "工具执行",
  completed: "结果整理",
  failed: "执行失败",
};
const defaultStageDetails: Record<TaskStatus, string> = {
  submitted: "前端已接收并提交任务，准备交给后端处理。",
  analyzing: "系统正在理解任务意图，并决定是否进入资料检索链路。",
  executing: "系统正在执行混合检索、重排、摘要生成或出题流程。",
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
  });
});

const canRetryLastTask = computed(() => status.value === "failed" && Boolean(lastSubmittedMessage.value));

function createWelcomeMessages(): MessageItem[] {
  return [
    {
      id: "welcome",
      role: "assistant",
      kind: "text",
      content: "### 欢迎\n\n你可以先上传学习资料，再让我围绕资料做追问、总结和出题。答错的题也会自动进入错题本。",
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
        result: task.result,
        sources: task.retrievedChunks,
      });
    }
  }

  messages.value = nextMessages;
  applyTaskRecordState(tasks[tasks.length - 1]);
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
  clearProgressTimers();
  activeSessionId.value = "";
  activeSessionTitle.value = "新会话";
  draft.value = defaultDraft;
  sessionError.value = "";
  documents.value = [];
  messages.value = createWelcomeMessages();
  resetInspectorState();
  resetDocumentFeedback();
}

function applyTemplate(prompt: string) {
  draft.value = prompt;
  composerError.value = "";
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

async function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  target.value = "";

  if (!file || !authStore.token) {
    return;
  }

  uploadingDocument.value = true;
  resetDocumentFeedback();

  try {
    const uploaded = await uploadDocument(file, authStore.token, activeSessionId.value || undefined);
    activeSessionId.value = uploaded.sessionId;
    documents.value = [...documents.value, uploaded];
    documentFeedback.value = `资料已上传：${uploaded.fileName}`;
    documentFeedbackType.value = "success";
    await loadSessionList();
    await openSession(uploaded.sessionId);
  } catch (error) {
    if (await handleAuthError(error)) {
      return;
    }
    documentFeedback.value = error instanceof Error ? error.message : "资料上传失败";
    documentFeedbackType.value = "error";
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
  } catch (error) {
    composerError.value = error instanceof Error ? error.message : "导出失败";
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

async function handleSubmit() {
  const message = draft.value.trim();
  if (submitting.value || checkingSession.value || loadingHistory.value) {
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

  messages.value.push({
    id: crypto.randomUUID(),
    role: "user",
    kind: "text",
    content: message,
  });

  submitting.value = true;
  composerError.value = "";
  intent.value = "";
  lastSubmittedMessage.value = message;
  startPendingProgress();

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
      result: response.result,
      sources: response.retrievedChunks,
    });
    draft.value = "";
    await loadSessionList();
    const currentSession = sessions.value.find((item) => item.sessionId === response.sessionId);
    activeSessionTitle.value = currentSession?.title ?? activeSessionTitle.value;
  } catch (error) {
    clearProgressTimers();
    if (await handleAuthError(error)) {
      return;
    }
    const messageText = error instanceof Error ? error.message : "请求失败";
    status.value = "failed";
    currentStatusLabel.value = stageLabelMap.failed;
    planSteps.value = [
      stageLabelMap.submitted,
      stageLabelMap.analyzing,
      "任务执行中断，请检查输入或稍后重试",
    ];
    composerError.value = "任务执行失败，可直接重试上一次任务。";
    messages.value.push({
      id: crypto.randomUUID(),
      role: "assistant",
      kind: "error",
      errorMessage: messageText,
      errorHint: "可以点击“重试上次任务”，或修改描述后重新发送。",
    });
  } finally {
    submitting.value = false;
  }
}

onMounted(() => {
  void validateSession();
});

onBeforeUnmount(() => {
  clearProgressTimers();
});
</script>
