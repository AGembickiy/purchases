<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">Панель управления</h1>
      <p class="page-subtitle">
        Обзор деятельности компании {{ companyStore.currentCompany?.name }}
      </p>
    </div>

    <!-- Статистические карточки -->
    <div class="content-section">
      <div class="content-grid content-grid-4">
        <div class="dashboard-card">
          <div class="dashboard-metric">
            <div class="dashboard-metric-value">{{ stats.users || 0 }}</div>
            <div class="dashboard-metric-label">Сотрудников</div>
          </div>
        </div>
        
        <div class="dashboard-card">
          <div class="dashboard-metric">
            <div class="dashboard-metric-value">{{ stats.orders || 0 }}</div>
            <div class="dashboard-metric-label">Заказов</div>
          </div>
        </div>
        
        <div class="dashboard-card">
          <div class="dashboard-metric">
            <div class="dashboard-metric-value">{{ stats.products || 0 }}</div>
            <div class="dashboard-metric-label">Товаров</div>
          </div>
        </div>
        
        <div class="dashboard-card">
          <div class="dashboard-metric">
            <div class="dashboard-metric-value">{{ stats.suppliers || 0 }}</div>
            <div class="dashboard-metric-label">Поставщиков</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Последние заказы -->
    <div class="content-section">
      <div class="card">
        <div class="card-header">
          <h3>Последние заказы</h3>
          <router-link to="/orders" class="btn btn-outline text-sm">
            Все заказы
          </router-link>
        </div>
        <div class="card-body">
          <div v-if="ordersLoading" class="text-center py-8">
            <div class="text-neutral-500">Загрузка...</div>
          </div>
          
          <div v-else-if="recentOrders.length === 0" class="text-center py-8 text-neutral-500">
            Заказов пока нет
          </div>
          
          <div v-else class="overflow-x-auto">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Номер</th>
                  <th>Описание</th>
                  <th>Статус</th>
                  <th>Сумма</th>
                  <th>Дата создания</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="order in recentOrders" :key="order.id">
                  <td class="font-medium">{{ order.number }}</td>
                  <td>{{ order.description || 'Без описания' }}</td>
                  <td>
                    <span :class="getStatusClass(order.status)" class="status-badge">
                      {{ getStatusText(order.status) }}
                    </span>
                  </td>
                  <td>
                    <span v-if="order.total_amount" class="font-medium">
                      {{ formatCurrency(order.total_amount) }}
                    </span>
                    <span v-else class="text-neutral-500">—</span>
                  </td>
                  <td class="text-neutral-600">
                    {{ formatDate(order.created_at) }}
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
import { useCompanyStore } from '@/stores/company'
import { useApi } from '@/composables/useApi'
import type { Order, OrderStatus } from '@/types'

const companyStore = useCompanyStore()

// Статистика
const stats = ref({
  users: 0,
  orders: 0,
  products: 0,
  suppliers: 0,
})

// Последние заказы
const recentOrders = ref<Order[]>([])
const ordersLoading = ref(false)

// API для загрузки данных
const { get: getStats } = useApi('/api/dashboard/stats/')
const { get: getOrders } = useApi('/api/orders/')

// Загрузка данных
const loadDashboardData = async () => {
  try {
    // Загружаем статистику
    const statsResponse = await getStats()
    if (statsResponse) {
      stats.value = statsResponse
    }

    // Загружаем последние заказы
    ordersLoading.value = true
    const ordersResponse = await getOrders('?limit=5&ordering=-created_at')
    if (ordersResponse?.results) {
      recentOrders.value = ordersResponse.results
    }
  } catch (error) {
    console.error('Ошибка загрузки данных дашборда:', error)
  } finally {
    ordersLoading.value = false
  }
}

// Утилиты для отображения
const getStatusClass = (status: OrderStatus): string => {
  const classes = {
    draft: 'status-draft',
    pending: 'status-pending',
    processing: 'status-processing',
    completed: 'status-completed',
    cancelled: 'status-cancelled',
    on_hold: 'status-on-hold',
  }
  return classes[status] || 'status-draft'
}

const getStatusText = (status: OrderStatus): string => {
  const texts = {
    draft: 'Черновик',
    pending: 'Ожидает',
    processing: 'В работе',
    completed: 'Завершен',
    cancelled: 'Отменен',
    on_hold: 'Приостановлен',
  }
  return texts[status] || 'Неизвестно'
}

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
  }).format(amount)
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('ru-RU')
}

// Инициализация
onMounted(() => {
  loadDashboardData()
})
</script>
