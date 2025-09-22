import { ref, computed } from 'vue'
import type { Ref } from 'vue'
import type { ApiResponse, PaginatedResponse } from '@/types'

export interface UseApiOptions {
  immediate?: boolean
  baseURL?: string
}

export function useApi<T = any>(url: string, options: UseApiOptions = {}) {
  const { immediate = false, baseURL = '/api' } = options
  
  // Состояние
  const data = ref<T | null>(null) as Ref<T | null>
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const isError = computed(() => error.value !== null)

  // Утилита для создания запросов
  const createRequest = (method: string, body?: any): RequestInit => {
    const headers: HeadersInit = {
      'X-CSRFToken': window.DJANGO_DATA?.csrf_token || '',
    }

    if (body && !(body instanceof FormData)) {
      headers['Content-Type'] = 'application/json'
    }

    return {
      method,
      headers,
      body: body instanceof FormData ? body : JSON.stringify(body),
    }
  }

  // Основной метод выполнения запроса
  const execute = async (
    requestUrl?: string, 
    requestOptions?: RequestInit
  ): Promise<T | null> => {
    const finalUrl = requestUrl || url
    const fullUrl = finalUrl.startsWith('http') ? finalUrl : `${baseURL}${finalUrl}`
    
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch(fullUrl, requestOptions)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const result = await response.json()
      data.value = result
      return result
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Неизвестная ошибка'
      error.value = errorMessage
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // HTTP методы
  const get = (requestUrl?: string) => 
    execute(requestUrl, createRequest('GET'))

  const post = (body?: any, requestUrl?: string) => 
    execute(requestUrl, createRequest('POST', body))

  const put = (body?: any, requestUrl?: string) => 
    execute(requestUrl, createRequest('PUT', body))

  const patch = (body?: any, requestUrl?: string) => 
    execute(requestUrl, createRequest('PATCH', body))

  const del = (requestUrl?: string) => 
    execute(requestUrl, createRequest('DELETE'))

  // Автоматическое выполнение при создании
  if (immediate) {
    get()
  }

  return {
    data,
    isLoading,
    error,
    isError,
    execute,
    get,
    post,
    put,
    patch,
    delete: del,
  }
}

// Специализированный хук для пагинированных данных
export function usePaginatedApi<T = any>(url: string, options: UseApiOptions = {}) {
  const api = useApi<PaginatedResponse<T>>(url, options)
  
  const items = computed(() => api.data.value?.results || [])
  const count = computed(() => api.data.value?.count || 0)
  const hasNext = computed(() => !!api.data.value?.next)
  const hasPrevious = computed(() => !!api.data.value?.previous)

  const loadNext = async () => {
    if (api.data.value?.next) {
      return api.get(api.data.value.next)
    }
  }

  const loadPrevious = async () => {
    if (api.data.value?.previous) {
      return api.get(api.data.value.previous)
    }
  }

  const loadPage = async (page: number) => {
    const separator = url.includes('?') ? '&' : '?'
    return api.get(`${url}${separator}page=${page}`)
  }

  return {
    ...api,
    items,
    count,
    hasNext,
    hasPrevious,
    loadNext,
    loadPrevious,
    loadPage,
  }
}

// Хук для работы с одним объектом (CRUD)
export function useResourceApi<T = any>(resourceName: string, baseURL = '/api') {
  const list = () => usePaginatedApi<T>(`${baseURL}/${resourceName}/`)
  
  const get = (id: number | string) => 
    useApi<T>(`${baseURL}/${resourceName}/${id}/`)
  
  const create = () => useApi<T>(`${baseURL}/${resourceName}/`)
  const update = (id: number | string) => 
    useApi<T>(`${baseURL}/${resourceName}/${id}/`)
  const remove = (id: number | string) => 
    useApi<T>(`${baseURL}/${resourceName}/${id}/`)

  return {
    list,
    get,
    create,
    update,
    remove,
  }
}
