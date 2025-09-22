<template>
  <div :class="cardClasses">
    <!-- Заголовок карточки -->
    <div v-if="title || $slots.header" class="card-header">
      <slot name="header">
        <h3 v-if="title" class="text-lg font-medium text-neutral-900">
          {{ title }}
        </h3>
      </slot>
    </div>
    
    <!-- Основное содержимое -->
    <div v-if="$slots.default" class="card-body">
      <slot />
    </div>
    
    <!-- Футер карточки -->
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

export interface CardProps {
  title?: string
  variant?: 'default' | 'bordered' | 'elevated' | 'flat'
  padding?: 'none' | 'sm' | 'md' | 'lg'
  hoverable?: boolean
  clickable?: boolean
}

const props = withDefaults(defineProps<CardProps>(), {
  variant: 'default',
  padding: 'md',
  hoverable: false,
  clickable: false,
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const cardClasses = computed(() => {
  const base = 'card'
  const classes = [base]
  
  // Варианты
  const variants = {
    default: 'bg-white rounded-xl shadow-soft border border-neutral-200',
    bordered: 'bg-white rounded-xl border-2 border-neutral-200',
    elevated: 'bg-white rounded-xl shadow-medium',
    flat: 'bg-white rounded-xl',
  }
  classes.push(variants[props.variant])
  
  // Интерактивность
  if (props.hoverable) {
    classes.push('transition-all duration-200 hover:shadow-medium hover:-translate-y-1')
  }
  
  if (props.clickable) {
    classes.push('cursor-pointer transition-all duration-200 hover:shadow-medium')
  }
  
  return classes.join(' ')
})

const handleClick = (event: MouseEvent) => {
  if (props.clickable) {
    emit('click', event)
  }
}
</script>
