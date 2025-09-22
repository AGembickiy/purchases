<template>
  <Teleport to="body">
    <Transition name="modal" appear>
      <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
        <div 
          :class="modalClasses"
          @click.stop
          role="dialog"
          aria-modal="true"
          :aria-labelledby="titleId"
        >
          <!-- Заголовок -->
          <div v-if="title || $slots.header" class="modal-header">
            <slot name="header">
              <h2 :id="titleId" class="text-xl font-semibold text-neutral-900">
                {{ title }}
              </h2>
            </slot>
            
            <button
              v-if="closable"
              type="button"
              class="modal-close"
              @click="close"
              aria-label="Закрыть модальное окно"
            >
              <span class="text-xl">✕</span>
            </button>
          </div>
          
          <!-- Содержимое -->
          <div class="modal-body">
            <slot />
          </div>
          
          <!-- Футер -->
          <div v-if="$slots.footer" class="modal-footer">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, useId, watchEffect } from 'vue'

export interface ModalProps {
  show: boolean
  title?: string
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  closable?: boolean
  closeOnOverlay?: boolean
  persistent?: boolean
}

const props = withDefaults(defineProps<ModalProps>(), {
  size: 'md',
  closable: true,
  closeOnOverlay: true,
  persistent: false,
})

const emit = defineEmits<{
  close: []
  'update:show': [value: boolean]
}>()

const titleId = useId()

const modalClasses = computed(() => {
  const base = 'modal-content bg-white rounded-xl shadow-hard'
  const classes = [base]
  
  // Размеры
  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-full mx-4',
  }
  classes.push(sizes[props.size])
  
  return classes.join(' ')
})

const close = () => {
  if (!props.persistent) {
    emit('close')
    emit('update:show', false)
  }
}

const handleOverlayClick = () => {
  if (props.closeOnOverlay) {
    close()
  }
}

// Блокируем скролл при открытом модальном окне
watchEffect(() => {
  if (props.show) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

// Обработка Escape
const handleEscape = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && props.show && props.closable) {
    close()
  }
}

watchEffect(() => {
  if (props.show) {
    document.addEventListener('keydown', handleEscape)
  } else {
    document.removeEventListener('keydown', handleEscape)
  }
})
</script>

<style scoped>
.modal-overlay {
  @apply fixed inset-0 z-50 flex items-center justify-center;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}

.modal-content {
  @apply relative w-full max-h-screen overflow-hidden;
}

.modal-header {
  @apply flex items-center justify-between px-6 py-4 border-b border-neutral-200;
}

.modal-close {
  @apply p-1 text-neutral-400 hover:text-neutral-600 transition-colors;
}

.modal-body {
  @apply px-6 py-4 max-h-96 overflow-y-auto;
}

.modal-footer {
  @apply px-6 py-4 border-t border-neutral-200 flex justify-end space-x-3;
}

/* Анимации */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.25s ease;
}

.modal-enter-active .modal-content,
.modal-leave-active .modal-content {
  transition: transform 0.25s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: scale(0.9) translateY(-20px);
}
</style>
