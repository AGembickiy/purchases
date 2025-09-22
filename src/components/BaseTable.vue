<template>
  <div class="overflow-x-auto">
    <table class="data-table">
      <!-- Заголовок -->
      <thead>
        <tr>
          <th 
            v-for="column in columns" 
            :key="column.key"
            :class="getHeaderClass(column)"
            @click="handleSort(column)"
          >
            <div class="flex items-center">
              <span>{{ column.title }}</span>
              <span v-if="column.sortable" class="ml-2 text-xs">
                <span v-if="sortKey === column.key">
                  {{ sortOrder === 'asc' ? '↑' : '↓' }}
                </span>
                <span v-else class="text-neutral-400">↕</span>
              </span>
            </div>
          </th>
        </tr>
      </thead>
      
      <!-- Тело таблицы -->
      <tbody>
        <tr v-if="loading" class="animate-pulse">
          <td :colspan="columns.length" class="text-center py-8">
            <div class="text-neutral-500">Загрузка...</div>
          </td>
        </tr>
        
        <tr v-else-if="sortedData.length === 0">
          <td :colspan="columns.length" class="text-center py-8 text-neutral-500">
            {{ emptyText }}
          </td>
        </tr>
        
        <tr 
          v-else
          v-for="(item, index) in sortedData" 
          :key="getRowKey(item, index)"
          :class="getRowClass(item, index)"
          @click="handleRowClick(item, index)"
        >
          <td 
            v-for="column in columns" 
            :key="column.key"
            :class="getCellClass(column)"
          >
            <slot 
              :name="column.key" 
              :item="item" 
              :value="getValue(item, column.key)"
              :index="index"
            >
              {{ formatValue(getValue(item, column.key), column) }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

export interface TableColumn {
  key: string
  title: string
  sortable?: boolean
  width?: string
  align?: 'left' | 'center' | 'right'
  format?: 'text' | 'number' | 'currency' | 'date' | 'custom'
}

export interface TableProps {
  columns: TableColumn[]
  data: any[]
  loading?: boolean
  emptyText?: string
  sortable?: boolean
  clickableRows?: boolean
  rowKey?: string | ((item: any) => string | number)
}

const props = withDefaults(defineProps<TableProps>(), {
  loading: false,
  emptyText: 'Нет данных',
  sortable: true,
  clickableRows: false,
  rowKey: 'id',
})

const emit = defineEmits<{
  rowClick: [item: any, index: number]
  sort: [key: string, order: 'asc' | 'desc']
}>()

// Состояние сортировки
const sortKey = ref<string>('')
const sortOrder = ref<'asc' | 'desc'>('asc')

// Отсортированные данные
const sortedData = computed(() => {
  if (!sortKey.value || !props.sortable) {
    return props.data
  }
  
  const sorted = [...props.data].sort((a, b) => {
    const aVal = getValue(a, sortKey.value)
    const bVal = getValue(b, sortKey.value)
    
    if (aVal === bVal) return 0
    if (aVal === null || aVal === undefined) return 1
    if (bVal === null || bVal === undefined) return -1
    
    const result = aVal < bVal ? -1 : 1
    return sortOrder.value === 'asc' ? result : -result
  })
  
  return sorted
})

// Методы
const getValue = (item: any, key: string): any => {
  return key.split('.').reduce((obj, k) => obj?.[k], item)
}

const getRowKey = (item: any, index: number): string | number => {
  if (typeof props.rowKey === 'function') {
    return props.rowKey(item)
  }
  return getValue(item, props.rowKey) || index
}

const handleSort = (column: TableColumn) => {
  if (!column.sortable || !props.sortable) return
  
  if (sortKey.value === column.key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = column.key
    sortOrder.value = 'asc'
  }
  
  emit('sort', sortKey.value, sortOrder.value)
}

const handleRowClick = (item: any, index: number) => {
  if (props.clickableRows) {
    emit('rowClick', item, index)
  }
}

const formatValue = (value: any, column: TableColumn): string => {
  if (value === null || value === undefined) return '—'
  
  switch (column.format) {
    case 'number':
      return new Intl.NumberFormat('ru-RU').format(value)
    case 'currency':
      return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
      }).format(value)
    case 'date':
      return new Date(value).toLocaleDateString('ru-RU')
    default:
      return String(value)
  }
}

// CSS классы
const getHeaderClass = (column: TableColumn): string => {
  const classes = []
  
  if (column.sortable && props.sortable) {
    classes.push('cursor-pointer hover:bg-neutral-100')
  }
  
  if (column.align) {
    classes.push(`text-${column.align}`)
  }
  
  return classes.join(' ')
}

const getRowClass = (item: any, index: number): string => {
  const classes = []
  
  if (props.clickableRows) {
    classes.push('cursor-pointer hover:bg-neutral-50')
  }
  
  return classes.join(' ')
}

const getCellClass = (column: TableColumn): string => {
  const classes = []
  
  if (column.align) {
    classes.push(`text-${column.align}`)
  }
  
  return classes.join(' ')
}
</script>
