<template>
  <div class="form-group">
    <label v-if="label" :for="inputId" class="form-label">
      {{ label }}
      <span v-if="required" class="text-error-500 ml-1">*</span>
    </label>
    
    <div class="relative">
      <input
        :id="inputId"
        v-model="inputValue"
        :type="type"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :class="inputClasses"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
      />
      
      <!-- Иконка -->
      <div v-if="icon" class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <span class="text-neutral-400 text-sm">{{ icon }}</span>
      </div>
      
      <!-- Кнопка очистки -->
      <button
        v-if="clearable && inputValue"
        type="button"
        class="absolute inset-y-0 right-0 pr-3 flex items-center"
        @click="clearInput"
      >
        <span class="text-neutral-400 hover:text-neutral-600 text-sm">✕</span>
      </button>
    </div>
    
    <!-- Сообщение об ошибке -->
    <div v-if="error" class="form-error">
      {{ error }}
    </div>
    
    <!-- Подсказка -->
    <div v-if="hint && !error" class="text-sm text-neutral-500 mt-1">
      {{ hint }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, useId } from 'vue'

export interface InputProps {
  modelValue?: string | number
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search'
  label?: string
  placeholder?: string
  disabled?: boolean
  readonly?: boolean
  required?: boolean
  error?: string
  hint?: string
  icon?: string
  clearable?: boolean
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<InputProps>(), {
  type: 'text',
  disabled: false,
  readonly: false,
  required: false,
  clearable: false,
  size: 'md',
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  input: [event: Event]
  blur: [event: FocusEvent]
  focus: [event: FocusEvent]
}>()

const inputId = useId()
const focused = ref(false)

const inputValue = computed({
  get: () => props.modelValue || '',
  set: (value) => emit('update:modelValue', value),
})

const inputClasses = computed(() => {
  const base = 'form-input-enhanced'
  const classes = [base]
  
  // Размеры
  const sizes = {
    sm: 'py-1.5 px-3 text-sm',
    md: 'py-2 px-4 text-sm', 
    lg: 'py-3 px-4 text-base',
  }
  classes.push(sizes[props.size])
  
  // Отступ для иконки
  if (props.icon) {
    classes.push('pl-10')
  }
  
  // Отступ для кнопки очистки
  if (props.clearable) {
    classes.push('pr-10')
  }
  
  // Состояние ошибки
  if (props.error) {
    classes.push('border-error-500 focus:ring-error-500')
  }
  
  // Состояние фокуса
  if (focused.value) {
    classes.push('ring-2')
  }
  
  return classes.join(' ')
})

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
  emit('input', event)
}

const handleBlur = (event: FocusEvent) => {
  focused.value = false
  emit('blur', event)
}

const handleFocus = (event: FocusEvent) => {
  focused.value = true
  emit('focus', event)
}

const clearInput = () => {
  emit('update:modelValue', '')
}
</script>
