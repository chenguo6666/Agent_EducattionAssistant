<!--
  LoginPage.vue - 用户登录/注册页面
  
  功能说明：
  - 支持登录和注册两种模式切换
  - 登录：输入账号（用户名或手机号）和密码
  - 注册：输入用户名、手机号和密码
  - 登录成功后自动跳转到聊天页面
  - 注册成功后自动登录并跳转
-->
<template>
  <main class="auth-layout">
    <ToastNotification
      :visible="toastVisible"
      :message="toastMessage"
      :type="toastType"
      @close="toastVisible = false"
    />
    
    <section class="auth-card">
      <!-- 应用介绍区域 -->
      <div>
        <p class="eyebrow">Sprint 1 / MVP</p>
        <h1>教育助手 AI Agent</h1>
        <p class="muted">先完成登录与基础对话链路，后续再接入完整 Agent 能力。</p>
      </div>

      <!-- 登录/注册表单 -->
      <form class="auth-form" @submit.prevent="handleSubmit">
        <!-- 注册模式：显示用户名和手机号输入框 -->
        <template v-if="isRegister">
          <label for="register-username">
            <span>用户名</span>
            <input id="register-username" v-model.trim="form.username" type="text" placeholder="student1" autocomplete="username" required />
          </label>

          <label for="register-phone">
            <span>手机号</span>
            <input id="register-phone" v-model.trim="form.phone" type="text" placeholder="13800000000" autocomplete="tel" required />
          </label>
        </template>

        <!-- 登录模式：只显示账号输入框 -->
        <label v-else for="login-account">
          <span>账号</span>
          <input id="login-account" v-model.trim="form.account" type="text" placeholder="student1 / 13800000000" autocomplete="username" required />
        </label>

        <!-- 密码输入框（登录和注册共用） -->
        <label :for="isRegister ? 'register-password' : 'login-password'">
          <span>密码</span>
          <input :id="isRegister ? 'register-password' : 'login-password'" v-model="form.password" type="password" :autocomplete="isRegister ? 'new-password' : 'current-password'" placeholder="请输入密码" required />
        </label>

        <!-- 提交按钮 -->
        <button class="primary-button" type="submit" :disabled="submitting">
          {{ submitting ? "提交中..." : isRegister ? "注册" : "登录" }}
        </button>
      </form>

<<<<<<< HEAD
=======
      <!-- 反馈信息（成功/错误提示） -->
      <p v-if="feedback" class="feedback" :class="{ success: feedbackType === 'success' }">{{ feedback }}</p>

      <!-- 模式切换按钮 -->
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
      <button class="secondary-button" type="button" @click="toggleMode">
        {{ isRegister ? "已有账号，去登录" : "没有账号，去注册" }}
      </button>
    </section>
  </main>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { login, register } from "@/api/auth";
import { useAuthStore } from "@/stores/auth";
import ToastNotification from "@/components/ToastNotification.vue";

const router = useRouter();
const authStore = useAuthStore();

/** 是否为注册模式（false = 登录模式） */
const isRegister = ref(false);
/** 提交状态，防止重复提交 */
const submitting = ref(false);
<<<<<<< HEAD

// Toast state
const toastVisible = ref(false);
const toastMessage = ref("");
const toastType = ref<"success" | "error" | "info">("info");

function showToast(message: string, type: "success" | "error" | "info" = "info") {
  toastMessage.value = message;
  toastType.value = type;
  toastVisible.value = true;
}

function hideToast() {
  toastVisible.value = false;
}
=======
/** 反馈消息文本 */
const feedback = ref("");
/** 反馈类型：error 或 success */
const feedbackType = ref<"error" | "success">("error");
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)

/**
 * 表单数据
 * - 登录模式使用 account
 * - 注册模式使用 username 和 phone
 */
const form = reactive({
  account: "student1",
  username: "student1",
  phone: "13800000000",
  password: "123456",
});

<<<<<<< HEAD
=======
/**
 * 重置反馈状态
 */
function resetFeedback() {
  feedback.value = "";
  feedbackType.value = "error";
}

/**
 * 切换登录/注册模式
 */
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
function toggleMode() {
  hideToast();
  isRegister.value = !isRegister.value;
}

/**
 * 登录并跳转到聊天页面
 * 
 * @param account - 账号
 * @param password - 密码
 */
async function loginAndRedirect(account: string, password: string) {
  // 调用登录 API
  const response = await login({ account, password });
  // 保存登录态到 Pinia store
  authStore.setSession(response);
<<<<<<< HEAD
  // Store login success flag for ChatPage to show toast
  sessionStorage.setItem('loginSuccess', 'true');
=======
  // 跳转到聊天页面
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
  await router.push("/chat");
}

/**
 * 处理表单提交
 * 
 * 核心逻辑：
 * 1. 判断当前模式（登录/注册）
 * 2. 调用相应 API
 * 3. 注册成功后自动执行登录
 * 4. 处理错误并显示反馈
 */
async function handleSubmit() {
  submitting.value = true;
  hideToast();

  try {
    if (isRegister.value) {
<<<<<<< HEAD
      // Registration - set flag before redirecting
=======
      // 注册模式
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
      await register({
        username: form.username,
        phone: form.phone,
        password: form.password,
      });
<<<<<<< HEAD
      sessionStorage.setItem('registerSuccess', 'true');
      isRegister.value = false;
=======
      feedback.value = "注册成功，正在进入工作台...";
      feedbackType.value = "success";
      // 注册成功后用用户名登录
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
      form.account = form.username;
      showToast("注册成功！请登录", "success");
      
    } else {
<<<<<<< HEAD
      // Login
      await loginAndRedirect(form.account, form.password);
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : "操作失败";
    showToast(message, "error");
=======
      // 登录模式
      await loginAndRedirect(form.account, form.password);
    }
  } catch (error) {
    // 显示错误消息
    feedback.value = error instanceof Error ? error.message : "操作失败";
    feedbackType.value = "error";
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
  } finally {
    submitting.value = false;
  }
}

/**
 * 组件挂载时检查是否已登录
 * 已登录则直接跳转到聊天页面
 */
onMounted(() => {
  // Check if user just logged in
  if (sessionStorage.getItem('loginSuccess') === 'true') {
    sessionStorage.removeItem('loginSuccess');
    showToast("登录成功！", "success");
  }
  
  // Check if user just registered
  if (sessionStorage.getItem('registerSuccess') === 'true') {
    sessionStorage.removeItem('registerSuccess');
    showToast("注册成功！请登录", "success");
  }
  
  if (authStore.isAuthenticated) {
    router.replace("/chat");
  }
});
</script>
