<template>
  <Teleport to="body">
    <Transition name="toast">
      <div v-if="visible" class="toast" :class="[`toast-${type}`]">
        <div class="toast-icon">
          <!-- Success icon -->
          <svg v-if="type === 'success'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M22 4L12 14.01l-3-3" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <!-- Error icon -->
          <svg v-else-if="type === 'error'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
          <!-- Info icon -->
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="16" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
        </div>
        <span class="toast-message">{{ message }}</span>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = withDefaults(defineProps<{
  message: string
  type?: 'success' | 'error' | 'info'
  duration?: number
  visible: boolean
}>(), {
  type: 'info',
  duration: 3000
})

const emit = defineEmits<{
  (e: 'close'): void
}>()

// Auto close after duration
watch(() => props.visible, (newVal) => {
  if (newVal) {
    setTimeout(() => {
      emit('close')
    }, props.duration)
  }
})
</script>

<style scoped>
.toast {
  position: fixed;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  border-radius: 16px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  font-size: 15px;
  font-weight: 500;
  max-width: 90vw;
  backdrop-filter: blur(12px);
}

.toast-success {
  background: linear-gradient(135deg, rgba(15, 123, 69, 0.95) 0%, rgba(16, 143, 82, 0.95) 100%);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.toast-error {
  background: linear-gradient(135deg, rgba(180, 35, 24, 0.95) 0%, rgba(211, 48, 37, 0.95) 100%);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.toast-info {
  background: linear-gradient(135deg, rgba(31, 111, 235, 0.95) 0%, rgba(22, 74, 159, 0.95) 100%);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.toast-icon {
  flex-shrink: 0;
  width: 22px;
  height: 22px;
}

.toast-icon svg {
  width: 100%;
  height: 100%;
}

.toast-message {
  line-height: 1.4;
}

/* Transition animations */
.toast-enter-active {
  animation: toast-in 0.3s ease-out;
}

.toast-leave-active {
  animation: toast-out 0.3s ease-in forwards;
}

@keyframes toast-in {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

@keyframes toast-out {
  from {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
  to {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
}
</style>
