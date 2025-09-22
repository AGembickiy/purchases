import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

// Импортируем компоненты страниц
const Dashboard = () => import('@/views/Dashboard.vue')
const Users = () => import('@/views/Users.vue')
const Products = () => import('@/views/Products.vue')
const Orders = () => import('@/views/Orders.vue')
const Suppliers = () => import('@/views/Suppliers.vue')
const Departments = () => import('@/views/Departments.vue')

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { 
      title: 'Панель управления',
      requiresAuth: true 
    }
  },
  {
    path: '/users',
    name: 'Users',
    component: Users,
    meta: { 
      title: 'Сотрудники',
      requiresAuth: true 
    }
  },
  {
    path: '/products',
    name: 'Products', 
    component: Products,
    meta: { 
      title: 'Товары',
      requiresAuth: true 
    }
  },
  {
    path: '/orders',
    name: 'Orders',
    component: Orders,
    meta: { 
      title: 'Заказы',
      requiresAuth: true 
    }
  },
  {
    path: '/suppliers',
    name: 'Suppliers',
    component: Suppliers,
    meta: { 
      title: 'Контрагенты',
      requiresAuth: true 
    }
  },
  {
    path: '/departments',
    name: 'Departments',
    component: Departments,
    meta: { 
      title: 'Подразделения',
      requiresAuth: true 
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Глобальная защита маршрутов
router.beforeEach((to, from, next) => {
  const requiresAuth = to.meta?.requiresAuth

  if (requiresAuth) {
    // Проверяем аутентификацию пользователя
    const isAuthenticated = window.DJANGO_DATA?.user?.is_authenticated

    if (!isAuthenticated) {
      // Перенаправляем на страницу входа Django
      window.location.href = '/companies/'
      return
    }
  }

  // Устанавливаем заголовок страницы
  if (to.meta?.title) {
    document.title = `${to.meta.title} - Система закупок`
  }

  next()
})

export default router
