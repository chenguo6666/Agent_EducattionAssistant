<template>
  <main class="auth-layout">
    <ToastNotification
      :visible="toastVisible"
      :message="toastMessage"
      :type="toastType"
      @close="toastVisible = false"
    />
    
    <section class="auth-card">
      <div>
        <p class="eyebrow">Sprint 1 / MVP</p>
        <h1>教育助手 AI Agent</h1>
        <p class="muted">先完成登录与基础对话链路，后续再接入完整 Agent 能力。</p>
      </div>

      <form class="auth-form" @submit.prevent="handleSubmit">
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

        <label v-else for="login-account">
          <span>账号</span>
          <input id="login-account" v-model.trim="form.account" type="text" placeholder="student1 / 13800000000" autocomplete="username" required />
        </label>

        <label :for="isRegister ? 'register-password' : 'login-password'">
          <span>密码</span>
          <input :id="isRegister ? 'register-password' : 'login-password'" v-model="form.password" type="password" :autocomplete="isRegister ? 'new-password' : 'current-password'" placeholder="请输入密码" required />
        </label>

        <button class="primary-button" type="submit" :disabled="submitting">
          {{ submitting ? "提交中..." : isRegister ? "注册" : "登录" }}
        </button>
      </form>

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

const isRegister = ref(false);
const submitting = ref(false);

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

const form = reactive({
  account: "student1",
  username: "student1",
  phone: "13800000000",
  password: "123456",
});

function toggleMode() {
  hideToast();
  isRegister.value = !isRegister.value;
}

async function loginAndRedirect(account: string, password: string) {
  const response = await login({
    account,
    password,
  });
  authStore.setSession(response);
  // Store login success flag for ChatPage to show toast
  sessionStorage.setItem('loginSuccess', 'true');
  await router.push("/chat");
}

async function handleSubmit() {
  submitting.value = true;
  hideToast();

  try {
    if (isRegister.value) {
      // Registration - set flag before redirecting
      await register({
        username: form.username,
        phone: form.phone,
        password: form.password,
      });
      sessionStorage.setItem('registerSuccess', 'true');
      isRegister.value = false;
      form.account = form.username;
      showToast("注册成功！请登录", "success");
      
    } else {
      // Login
      await loginAndRedirect(form.account, form.password);
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : "操作失败";
    showToast(message, "error");
  } finally {
    submitting.value = false;
  }
}

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
