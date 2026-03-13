<template>
  <main class="chat-layout">
    <aside class="sidebar-card">
      <p class="eyebrow">教育场景 Agent</p>
      <h1>对话工作台</h1>
      <p class="muted">当前阶段先验证 Sprint 1 主链路：输入任务、识别意图、调用 Mock Tool、返回结果。</p>

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

      <div class="sidebar-actions">
        <button class="secondary-button button-small" type="button" @click="clearConversation">清空会话</button>
        <button class="secondary-button button-small" type="button" @click="logout">退出登录</button>
      </div>

      <section class="history-panel">
        <div class="history-panel-header">
          <p class="status-label">任务历史</p>
          <div class="history-panel-actions">
            <button class="secondary-button button-small" type="button" @click="toggleHistoryView">
              {{ historyView === "starred" ? "显示全部" : "仅收藏" }}
            </button>
            <button class="secondary-button button-small" type="button" @click="clearHistory" :disabled="taskHistory.length === 0">
              清空历史
            </button>
          </div>
        </div>

        <div v-if="visibleHistory.length === 0" class="history-empty muted">暂无历史任务</div>

        <div v-else class="history-list">
          <article v-for="item in visibleHistory" :key="item.id" class="history-item">
            <div class="history-item-main">
              <button class="history-star" type="button" :class="{ active: item.starred }" @click="toggleStar(item.id)">
                {{ item.starred ? "★" : "☆" }}
              </button>

              <div class="history-item-content">
                <p class="history-item-title">{{ item.title }}</p>
                <p class="history-item-meta">
                  <span>{{ formatHistoryTime(item.createdAt) }}</span>
                  <span>·</span>
                  <span>{{ historyStatusLabel(item.status) }}</span>
                  <template v-if="item.intent">
                    <span>·</span>
                    <span>{{ intentLabel(item.intent) }}</span>
                  </template>
                </p>
              </div>
            </div>

            <div class="history-item-actions">
              <button class="secondary-button button-small" type="button" @click="fillFromHistory(item.id)">回填</button>
              <button class="primary-button button-small" type="button" @click="rerunFromHistory(item.id)" :disabled="submitting || checkingSession">
                重跑
              </button>
            </div>
          </article>
        </div>
      </section>
    </aside>

    <section class="chat-card">
      <div class="message-list">
        <template v-for="message in messages" :key="message.id">
          <MessageBubble
            v-if="message.kind === 'text'"
            :role="message.role"
            :content="message.content ?? ''"
          />
          <TaskResultCard
            v-else-if="message.kind === 'result'"
            :intent="message.intent ?? 'unknown'"
            :prompt="message.prompt"
            :result="message.result!"
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
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { fetchMe } from "@/api/auth";
import { executeTask } from "@/api/chat";
import MessageBubble from "@/components/MessageBubble.vue";
import TaskErrorCard from "@/components/TaskErrorCard.vue";
import TaskResultCard from "@/components/TaskResultCard.vue";
import { useAuthStore } from "@/stores/auth";
import type { ChatResponse, ChatResult, TaskStage, TaskStatus } from "@/types/chat";

type MessageKind = "text" | "result" | "error";
interface MessageItem {
  id: string;
  role: "user" | "assistant";
  kind: MessageKind;
  content?: string;
  result?: ChatResult;
  intent?: string;
  prompt?: string;
  errorMessage?: string;
  errorHint?: string;
}

type HistoryStatus = TaskStatus | "idle";
type HistoryView = "all" | "starred";

interface TaskHistoryItem {
  id: string;
  taskId?: string;
  title: string;
  prompt: string;
  createdAt: number;
  status: HistoryStatus;
  intent?: string;
  starred: boolean;
}

type PersistedChatState = {
  version: 1;
  draft: string;
  messages: MessageItem[];
  status: HistoryStatus;
  intent: string;
  planSteps: string[];
  currentStatusLabel: string;
  lastSubmittedMessage: string;
  taskHistory: TaskHistoryItem[];
  historyView: HistoryView;
};

const router = useRouter();
const authStore = useAuthStore();

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
const taskHistory = ref<TaskHistoryItem[]>([]);
const historyView = ref<HistoryView>("all");

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
];

const stageLabelMap: Record<TaskStatus, string> = {
  submitted: "任务已提交",
  analyzing: "分析中",
  executing: "执行中",
  completed: "已完成",
  failed: "执行失败",
};
const historyStatusMap: Record<HistoryStatus, string> = {
  idle: "等待提交",
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
  });
});

const canRetryLastTask = computed(() => status.value === "failed" && Boolean(lastSubmittedMessage.value));
const visibleHistory = computed(() => {
  const source = historyView.value === "starred" ? taskHistory.value.filter((item) => item.starred) : taskHistory.value;
  return source.slice().sort((a, b) => b.createdAt - a.createdAt).slice(0, 24);
});
const persistKey = computed(() => {
  if (!authStore.user?.id) {
    return "";
  }
  return `education-agent-chat-state-v1:${authStore.user.id}`;
});
let persistTimer = 0;

function intentLabel(intentValue: string) {
  const map: Record<string, string> = {
    summary: "仅摘要",
    quiz: "仅出题",
    summary_and_quiz: "摘要 + 出题",
    unknown: "兜底处理",
  };
  return map[intentValue] ?? intentValue;
}

function historyStatusLabel(value: HistoryStatus) {
  return historyStatusMap[value] ?? value;
}

function formatHistoryTime(epochMs: number) {
  const d = new Date(epochMs);
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  const hh = String(d.getHours()).padStart(2, "0");
  const mi = String(d.getMinutes()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd} ${hh}:${mi}`;
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

function logout() {
  clearProgressTimers();
  authStore.clearSession();
  router.push("/login");
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
  } catch {
    authStore.clearSession();
    router.replace("/login");
  } finally {
    checkingSession.value = false;
  }
}

function applyTemplate(prompt: string) {
  draft.value = prompt;
  composerError.value = "";
}

function retryLastTask() {
  if (!lastSubmittedMessage.value || submitting.value) {
    return;
  }

  draft.value = lastSubmittedMessage.value;
  handleSubmit();
}

function clearConversation() {
  clearProgressTimers();
  composerError.value = "";
  draft.value = "";
  intent.value = "";
  planSteps.value = [];
  status.value = "idle";
  currentStatusLabel.value = "等待提交";
  lastSubmittedMessage.value = "";
  messages.value = [
    {
      id: "welcome",
      role: "assistant",
      kind: "text",
      content: "### 欢迎\n\n你可以直接输入学习任务，我会先按 Sprint 1 的能力返回摘要、题目或综合结果。",
    },
  ];
}

function clearHistory() {
  taskHistory.value = [];
}

function toggleHistoryView() {
  historyView.value = historyView.value === "starred" ? "all" : "starred";
}

function toggleStar(id: string) {
  const item = taskHistory.value.find((entry) => entry.id === id);
  if (!item) {
    return;
  }
  item.starred = !item.starred;
}

function fillFromHistory(id: string) {
  const item = taskHistory.value.find((entry) => entry.id === id);
  if (!item) {
    return;
  }
  draft.value = item.prompt;
  composerError.value = "";
}

function rerunFromHistory(id: string) {
  const item = taskHistory.value.find((entry) => entry.id === id);
  if (!item || submitting.value || checkingSession.value) {
    return;
  }
  draft.value = item.prompt;
  composerError.value = "";
  handleSubmit();
}

function trimMessages(items: MessageItem[]) {
  const limit = 80;
  if (items.length <= limit) {
    return items;
  }
  const welcome = items[0]?.id === "welcome" ? [items[0]] : [];
  return [...welcome, ...items.slice(-(limit - welcome.length))];
}

function trimHistory(items: TaskHistoryItem[]) {
  const limit = 60;
  return items.slice().sort((a, b) => b.createdAt - a.createdAt).slice(0, limit);
}

function persistStateNow() {
  if (!persistKey.value) {
    return;
  }

  const payload: PersistedChatState = {
    version: 1,
    draft: draft.value,
    messages: trimMessages(messages.value),
    status: status.value,
    intent: intent.value,
    planSteps: planSteps.value,
    currentStatusLabel: currentStatusLabel.value,
    lastSubmittedMessage: lastSubmittedMessage.value,
    taskHistory: trimHistory(taskHistory.value),
    historyView: historyView.value,
  };

  try {
    window.localStorage.setItem(persistKey.value, JSON.stringify(payload));
  } catch {
    // Ignore localStorage quota or privacy-mode failures.
  }
}

function schedulePersistState() {
  if (!persistKey.value) {
    return;
  }

  if (persistTimer) {
    window.clearTimeout(persistTimer);
  }

  persistTimer = window.setTimeout(() => {
    persistTimer = 0;
    persistStateNow();
  }, 200);
}

function loadPersistedState() {
  if (!persistKey.value) {
    return;
  }

  const raw = window.localStorage.getItem(persistKey.value);
  if (!raw) {
    return;
  }

  try {
    const parsed = JSON.parse(raw) as PersistedChatState;
    if (parsed.version !== 1) {
      return;
    }

    draft.value = typeof parsed.draft === "string" ? parsed.draft : draft.value;
    messages.value = Array.isArray(parsed.messages) && parsed.messages.length > 0 ? parsed.messages : messages.value;
    status.value = parsed.status ?? status.value;
    intent.value = typeof parsed.intent === "string" ? parsed.intent : intent.value;
    planSteps.value = Array.isArray(parsed.planSteps) ? parsed.planSteps : planSteps.value;
    currentStatusLabel.value = typeof parsed.currentStatusLabel === "string" ? parsed.currentStatusLabel : currentStatusLabel.value;
    lastSubmittedMessage.value = typeof parsed.lastSubmittedMessage === "string" ? parsed.lastSubmittedMessage : lastSubmittedMessage.value;
    taskHistory.value = Array.isArray(parsed.taskHistory) ? parsed.taskHistory : [];
    historyView.value = parsed.historyView === "starred" ? "starred" : "all";
  } catch {
    // Ignore corrupted local state.
  }
}

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

  const historyId = crypto.randomUUID();
  taskHistory.value.push({
    id: historyId,
    title: message.slice(0, 40) + (message.length > 40 ? "..." : ""),
    prompt: message,
    createdAt: Date.now(),
    status: "submitted",
    starred: false,
  });

  try {
    const response = await executeTask(message, authStore.token);
    clearProgressTimers();
    intent.value = response.intent;
    applyCompletedTimeline(response);

    const historyItem = taskHistory.value.find((item) => item.id === historyId);
    if (historyItem) {
      historyItem.taskId = response.taskId;
      historyItem.status = response.status;
      historyItem.intent = response.intent;
    }

    messages.value.push({
      id: response.taskId,
      role: "assistant",
      kind: "result",
      intent: response.intent,
      prompt: message,
      result: response.result,
    });
    draft.value = "";
  } catch (error) {
    clearProgressTimers();
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
      errorHint: sessionExpired ? "请重新登录后再次提交任务。" : "可以点击“重试上次任务”，或修改描述后重新发送。",
    });

    const historyItem = taskHistory.value.find((item) => item.id === historyId);
    if (historyItem) {
      historyItem.status = "failed";
    }

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

onMounted(() => {
  void (async () => {
    await validateSession();
    loadPersistedState();
  })();
});

onBeforeUnmount(() => {
  clearProgressTimers();
  if (persistTimer) {
    window.clearTimeout(persistTimer);
    persistTimer = 0;
  }
  persistStateNow();
});

watch(
  [draft, messages, status, intent, planSteps, currentStatusLabel, lastSubmittedMessage, taskHistory, historyView],
  () => {
    schedulePersistState();
  },
  { deep: true },
);
</script>
