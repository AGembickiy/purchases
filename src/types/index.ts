// Типы пользователя
export interface User {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
  is_authenticated: boolean
  is_active?: boolean
  date_joined?: string
}

// Типы компании
export interface Company {
  id: number
  name: string
  slug: string
  description?: string
  created_at?: string
  updated_at?: string
}

// Типы профиля пользователя
export interface UserProfile {
  id: number
  user: User
  phone_number?: string
  position?: string
  department?: Department
  avatar?: string
}

// Типы подразделения
export interface Department {
  id: number
  name: string
  description?: string
  parent?: Department
  company: Company
  created_at?: string
  updated_at?: string
}

// Типы товара
export interface Product {
  id: number
  name: string
  description?: string
  sku: string
  category?: ProductCategory
  unit: string
  price?: number
  company: Company
  is_active: boolean
  created_at?: string
  updated_at?: string
}

// Типы категории товара
export interface ProductCategory {
  id: number
  name: string
  description?: string
  parent?: ProductCategory
  company: Company
}

// Типы поставщика
export interface Supplier {
  id: number
  name: string
  contact_person?: string
  email?: string
  phone?: string
  address?: string
  company: Company
  is_active: boolean
  created_at?: string
  updated_at?: string
}

// Типы заказа
export interface Order {
  id: number
  number: string
  status: OrderStatus
  priority: OrderPriority
  description?: string
  requested_by: User
  assigned_to?: User
  department?: Department
  supplier?: Supplier
  total_amount?: number
  company: Company
  created_at?: string
  updated_at?: string
  items: OrderItem[]
}

// Типы элемента заказа
export interface OrderItem {
  id: number
  order: number
  product: Product
  quantity: number
  unit_price?: number
  total_price?: number
  notes?: string
}

// Перечисления
export enum OrderStatus {
  DRAFT = 'draft',
  PENDING = 'pending', 
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
  ON_HOLD = 'on_hold'
}

export enum OrderPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent'
}

// Типы API ответов
export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
}

export interface PaginatedResponse<T> {
  count: number
  next?: string
  previous?: string
  results: T[]
}

// Типы форм
export interface LoginForm {
  username: string
  password: string
}

export interface UserForm {
  username: string
  email: string
  first_name: string
  last_name: string
  password?: string
  is_active: boolean
}

export interface ProductForm {
  name: string
  description?: string
  sku: string
  category?: number
  unit: string
  price?: number
  is_active: boolean
}

export interface OrderForm {
  description?: string
  priority: OrderPriority
  department?: number
  supplier?: number
  items: OrderItemForm[]
}

export interface OrderItemForm {
  product: number
  quantity: number
  unit_price?: number
  notes?: string
}

// Типы состояний
export interface LoadingState {
  [key: string]: boolean
}

export interface ErrorState {
  [key: string]: string | null
}
