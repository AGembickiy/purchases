import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, UserProfile } from '@/types'

export const useUserStore = defineStore('user', () => {
  // Состояние
  const user = ref<User | null>(null)
  const profile = ref<UserProfile | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Геттеры
  const isAuthenticated = computed(() => user.value?.is_authenticated || false)
  const fullName = computed(() => {
    if (!user.value) return ''
    return `${user.value.first_name} ${user.value.last_name}`.trim() || user.value.username
  })

  // Действия
  const setUser = (userData: User) => {
    user.value = userData
    error.value = null
  }

  const setProfile = (profileData: UserProfile) => {
    profile.value = profileData
  }

  const clearUser = () => {
    user.value = null
    profile.value = null
    error.value = null
  }

  const setLoading = (loading: boolean) => {
    isLoading.value = loading
  }

  const setError = (errorMessage: string | null) => {
    error.value = errorMessage
  }

  // API методы
  const fetchProfile = async () => {
    if (!user.value) return

    setLoading(true)
    try {
      const response = await fetch('/api/users/profile/', {
        headers: {
          'X-CSRFToken': window.DJANGO_DATA?.csrf_token || '',
        },
      })
      
      if (response.ok) {
        const profileData = await response.json()
        setProfile(profileData)
      } else {
        throw new Error('Ошибка загрузки профиля')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Неизвестная ошибка')
    } finally {
      setLoading(false)
    }
  }

  const updateProfile = async (profileData: Partial<UserProfile>) => {
    if (!user.value) return

    setLoading(true)
    try {
      const response = await fetch('/api/users/profile/', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': window.DJANGO_DATA?.csrf_token || '',
        },
        body: JSON.stringify(profileData),
      })
      
      if (response.ok) {
        const updatedProfile = await response.json()
        setProfile(updatedProfile)
      } else {
        throw new Error('Ошибка обновления профиля')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Неизвестная ошибка')
    } finally {
      setLoading(false)
    }
  }

  const logout = async () => {
    try {
      await fetch('/api/auth/logout/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': window.DJANGO_DATA?.csrf_token || '',
        },
      })
      
      clearUser()
      // Перенаправляем на страницу входа Django
      window.location.href = '/companies/'
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка выхода')
    }
  }

  return {
    // Состояние
    user,
    profile,
    isLoading,
    error,
    
    // Геттеры
    isAuthenticated,
    fullName,
    
    // Действия
    setUser,
    setProfile,
    clearUser,
    setLoading,
    setError,
    fetchProfile,
    updateProfile,
    logout,
  }
})
