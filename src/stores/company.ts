import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Company } from '@/types'

export const useCompanyStore = defineStore('company', () => {
  // Состояние
  const currentCompany = ref<Company | null>(null)
  const companies = ref<Company[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Геттеры
  const hasCompany = computed(() => currentCompany.value !== null)
  const companySlug = computed(() => currentCompany.value?.slug || '')

  // Действия
  const setCurrentCompany = (company: Company) => {
    currentCompany.value = company
    error.value = null
  }

  const setCompanies = (companiesList: Company[]) => {
    companies.value = companiesList
  }

  const clearCompany = () => {
    currentCompany.value = null
    companies.value = []
    error.value = null
  }

  const setLoading = (loading: boolean) => {
    isLoading.value = loading
  }

  const setError = (errorMessage: string | null) => {
    error.value = errorMessage
  }

  // API методы
  const fetchCompanies = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/companies/', {
        headers: {
          'X-CSRFToken': window.DJANGO_DATA?.csrf_token || '',
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setCompanies(data.results || data)
      } else {
        throw new Error('Ошибка загрузки компаний')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Неизвестная ошибка')
    } finally {
      setLoading(false)
    }
  }

  const fetchCompanyDetails = async (slug: string) => {
    setLoading(true)
    try {
      const response = await fetch(`/api/companies/${slug}/`, {
        headers: {
          'X-CSRFToken': window.DJANGO_DATA?.csrf_token || '',
        },
      })
      
      if (response.ok) {
        const company = await response.json()
        setCurrentCompany(company)
      } else {
        throw new Error('Ошибка загрузки данных компании')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Неизвестная ошибка')
    } finally {
      setLoading(false)
    }
  }

  const updateCompany = async (companyData: Partial<Company>) => {
    if (!currentCompany.value) return

    setLoading(true)
    try {
      const response = await fetch(`/api/companies/${currentCompany.value.slug}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': window.DJANGO_DATA?.csrf_token || '',
        },
        body: JSON.stringify(companyData),
      })
      
      if (response.ok) {
        const updatedCompany = await response.json()
        setCurrentCompany(updatedCompany)
      } else {
        throw new Error('Ошибка обновления компании')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Неизвестная ошибка')
    } finally {
      setLoading(false)
    }
  }

  return {
    // Состояние
    currentCompany,
    companies,
    isLoading,
    error,
    
    // Геттеры
    hasCompany,
    companySlug,
    
    // Действия
    setCurrentCompany,
    setCompanies,
    clearCompany,
    setLoading,
    setError,
    fetchCompanies,
    fetchCompanyDetails,
    updateCompany,
  }
})
