<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">Сотрудники</h1>
      <p class="page-subtitle">Управление пользователями компании</p>
      
      <div class="flex items-center space-x-4 mt-4">
        <button @click="loadUsers" :disabled="isLoading" class="btn btn-secondary">
          {{ isLoading ? 'Загрузка...' : 'Обновить' }}
        </button>
        <button @click="showCreateModal = true" class="btn btn-primary">
          Добавить сотрудника
        </button>
      </div>
    </div>

    <!-- Фильтры -->
    <div class="content-section">
      <div class="card">
        <div class="card-body">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="form-label">Поиск</label>
              <input 
                v-model="filters.search" 
                @input="debouncedSearch"
                type="text" 
                class="form-input-enhanced"
                placeholder="Имя, email или должность...">
            </div>
            <div>
              <label class="form-label">Подразделение</label>
              <select v-model="filters.department" @change="applyFilters" class="form-select">
                <option value="">Все подразделения</option>
                <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                  {{ dept.name }}
                </option>
              </select>
            </div>
            <div>
              <label class="form-label">Статус</label>
              <select v-model="filters.active" @change="applyFilters" class="form-select">
                <option value="">Все</option>
                <option value="true">Активные</option>
                <option value="false">Неактивные</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Список пользователей -->
    <div class="content-section">
      <div class="card">
        <div class="card-header">
          <h3>Список сотрудников</h3>
          <span class="text-sm text-neutral-500">
            Всего: {{ totalUsers }}
          </span>
        </div>
        <div class="card-body">
          <div v-if="isLoading" class="text-center py-8">
            <div class="text-neutral-500">Загрузка сотрудников...</div>
          </div>
          
          <div v-else-if="users.length === 0" class="text-center py-8 text-neutral-500">
            Сотрудники не найдены
          </div>
          
          <div v-else class="overflow-x-auto">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Сотрудник</th>
                  <th>Email</th>
                  <th>Должность</th>
                  <th>Подразделение</th>
                  <th>Статус</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in users" :key="user.id">
                  <td>
                    <div class="flex items-center">
                      <div class="w-8 h-8 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-medium">
                        {{ getUserInitials(user) }}
                      </div>
                      <div class="ml-3">
                        <div class="font-medium">{{ getUserFullName(user) }}</div>
                        <div class="text-sm text-neutral-500">@{{ user.username }}</div>
                      </div>
                    </div>
                  </td>
                  <td>{{ user.email }}</td>
                  <td>{{ user.profile?.position || '—' }}</td>
                  <td>{{ user.profile?.department?.name || '—' }}</td>
                  <td>
                    <span :class="user.is_active ? 'badge-success' : 'badge-secondary'" class="badge">
                      {{ user.is_active ? 'Активен' : 'Неактивен' }}
                    </span>
                  </td>
                  <td>
                    <div class="flex items-center space-x-2">
                      <button @click="editUser(user)" class="btn-action btn-action-edit">
                        Изменить
                      </button>
                      <button 
                        @click="toggleUserStatus(user)" 
                        :class="user.is_active ? 'btn-action-delete' : 'btn-action-edit'"
                        class="btn-action">
                        {{ user.is_active ? 'Деактивировать' : 'Активировать' }}
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { usePaginatedApi } from '@/composables/useApi'
import type { User, Department } from '@/types'

// Состояние
const users = ref<User[]>([])
const departments = ref<Department[]>([])
const isLoading = ref(false)
const showCreateModal = ref(false)
const totalUsers = ref(0)

// Фильтры
const filters = ref({
  search: '',
  department: '',
  active: '',
})

// API
const usersApi = usePaginatedApi<User>('/api/users/')

// Методы
const loadUsers = async () => {
  isLoading.value = true
  try {
    const params = new URLSearchParams()
    if (filters.value.search) params.append('search', filters.value.search)
    if (filters.value.department) params.append('department', filters.value.department)
    if (filters.value.active) params.append('is_active', filters.value.active)
    
    const queryString = params.toString()
    const url = queryString ? `/api/users/?${queryString}` : '/api/users/'
    
    await usersApi.get(url)
    users.value = usersApi.items.value
    totalUsers.value = usersApi.count.value
  } catch (error) {
    console.error('Ошибка загрузки пользователей:', error)
  } finally {
    isLoading.value = false
  }
}

const loadDepartments = async () => {
  try {
    const response = await fetch('/api/departments/')
    if (response.ok) {
      const data = await response.json()
      departments.value = data.results || data
    }
  } catch (error) {
    console.error('Ошибка загрузки подразделений:', error)
  }
}

const applyFilters = () => {
  loadUsers()
}

// Дебаунс для поиска
let searchTimeout: ReturnType<typeof setTimeout>
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    applyFilters()
  }, 300)
}

const editUser = (user: User) => {
  // TODO: Открыть модальное окно редактирования
  console.log('Редактирование пользователя:', user)
}

const toggleUserStatus = async (user: User) => {
  try {
    const response = await fetch(`/api/users/${user.id}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': window.DJANGO_DATA?.csrf_token || '',
      },
      body: JSON.stringify({
        is_active: !user.is_active
      }),
    })
    
    if (response.ok) {
      const updatedUser = await response.json()
      const index = users.value.findIndex(u => u.id === user.id)
      if (index !== -1) {
        users.value[index] = updatedUser
      }
    }
  } catch (error) {
    console.error('Ошибка изменения статуса пользователя:', error)
  }
}

// Утилиты
const getUserFullName = (user: User): string => {
  return `${user.first_name} ${user.last_name}`.trim() || user.username
}

const getUserInitials = (user: User): string => {
  if (user.first_name && user.last_name) {
    return `${user.first_name[0]}${user.last_name[0]}`
  }
  return user.username.substring(0, 2).toUpperCase()
}

// Инициализация
onMounted(() => {
  loadUsers()
  loadDepartments()
})
</script>
