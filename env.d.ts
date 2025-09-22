/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// Расширяем интерфейс window для Django данных
declare global {
  interface Window {
    DJANGO_DATA?: {
      user?: {
        id: number
        username: string
        first_name: string
        last_name: string
        email: string
        is_authenticated: boolean
      }
      company?: {
        id: number
        name: string
        slug: string
      }
      csrf_token?: string
      api_base_url?: string
    }
  }
}

export {}
