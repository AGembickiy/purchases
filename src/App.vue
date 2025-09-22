<template>
  <div id="app" class="min-h-screen bg-neutral-50">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useCompanyStore } from '@/stores/company'

const userStore = useUserStore()
const companyStore = useCompanyStore()

onMounted(() => {
  // Инициализируем данные из Django если они доступны
  if (window.DJANGO_DATA) {
    if (window.DJANGO_DATA.user) {
      userStore.setUser(window.DJANGO_DATA.user)
    }
    if (window.DJANGO_DATA.company) {
      companyStore.setCurrentCompany(window.DJANGO_DATA.company)
    }
  }
})
</script>
