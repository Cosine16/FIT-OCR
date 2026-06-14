<script setup lang="ts">
import { h, ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NIcon } from 'naive-ui'
import {
  SpeedometerOutline, DocumentTextOutline, ImagesOutline,
  BarChartOutline, LogOutOutline, MenuOutline
} from '@vicons/ionicons5'

const router = useRouter()
const route = useRoute()
const collapsed = ref(false)

const menuItems = [
  { label: '仪表盘', key: '/dashboard', icon: SpeedometerOutline },
  { label: '识别记录', key: '/records', icon: DocumentTextOutline },
  { label: '图片管理', key: '/images', icon: ImagesOutline },
  { label: '调用统计', key: '/stats', icon: BarChartOutline },
]

const currentKey = computed(() => route.path)

function renderIcon(icon: any) {
  return () => h(NIcon, null, { default: () => h(icon) })
}

function doLogout() {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<template>
  <n-layout has-sider class="layout">
    <n-layout-sider bordered collapse-mode="width" :collapsed-width="64" :width="220" :collapsed="collapsed">
      <div class="logo">
        <span v-if="!collapsed">📐 FIT-OCR Admin</span>
        <span v-else>📐</span>
      </div>
      <n-menu
        :value="currentKey"
        :collapsed="collapsed"
        :collapsed-width="64"
        :options="menuItems.map(m => ({ label: m.label, key: m.key, icon: renderIcon(m.icon) }))"
        @update:value="(k: string) => router.push(k)"
      />
    </n-layout-sider>
    <n-layout>
      <n-layout-header bordered class="header">
        <n-space align="center">
          <n-button quaternary @click="collapsed = !collapsed">
            <n-icon :component="MenuOutline" />
          </n-button>
          <n-divider vertical />
          <n-button quaternary @click="doLogout">
            <n-icon :component="LogOutOutline" /> 退出
          </n-button>
        </n-space>
      </n-layout-header>
      <n-layout-content class="content">
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<style scoped>
.layout { height: 100vh; }
.logo {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  color: var(--n-text-color);
  border-bottom: 1px solid var(--n-border-color);
  overflow: hidden;
  white-space: nowrap;
}
.header {
  height: 56px;
  display: flex;
  align-items: center;
  padding: 0 16px;
}
.content {
  padding: 24px;
  overflow: auto;
}
</style>
