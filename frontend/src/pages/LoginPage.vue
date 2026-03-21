<template>
  <main class="auth-layout">
    <section class="auth-card">
      <div>
        <p class="eyebrow">Education Agent</p>
        <h1>教育助手 AI Agent</h1>
        <p class="muted">上传学习资料后即可进行总结、出题、资料追问与错题整理。</p>
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

      <p v-if="feedback" class="feedback" :class="{ success: feedbackType === 'success' }">{{ feedback }}</p>

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

const router = useRouter();
const authStore = useAuthStore();

const isRegister = ref(false);
const submitting = ref(false);
const feedback = ref("");
const feedbackType = ref<"error" | "success">("error");

const form = reactive({
  account: "student1",
  username: "student1",
  phone: "13800000000",
  password: "123456",
});

function resetFeedback() {
  feedback.value = "";
  feedbackType.value = "error";
}

function toggleMode() {
  isRegister.value = !isRegister.value;
  resetFeedback();
}

async function loginAndRedirect(account: string, password: string) {
  const response = await login({
    account,
    password,
  });
  authStore.setSession(response);
  await router.push("/chat");
}

async function handleSubmit() {
  submitting.value = true;
  resetFeedback();

  try {
    if (isRegister.value) {
      await register({
        username: form.username,
        phone: form.phone,
        password: form.password,
      });
      feedback.value = "注册成功，正在进入工作台...";
      feedbackType.value = "success";
      form.account = form.username;
      await loginAndRedirect(form.username, form.password);
    } else {
      await loginAndRedirect(form.account, form.password);
    }
  } catch (error) {
    feedback.value = error instanceof Error ? error.message : "操作失败";
    feedbackType.value = "error";
  } finally {
    submitting.value = false;
  }
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    router.replace("/chat");
  }
});
</script>
