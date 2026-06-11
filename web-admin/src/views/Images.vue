<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import api from '@/api'

const message = useMessage()
const images = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20

async function load() {
  const res = await api.get('/images', { params: { page: page.value, page_size: pageSize } })
  images.value = res.data.items
  total.value = res.data.total
}

async function delImage(filename: string) {
  await api.delete(`/images/${filename}`)
  message.success('已删除')
  load()
}

onMounted(load)
</script>

<template>
  <div>
    <h2 style="margin-top:0">图片管理</h2>

    <n-grid :cols="4" :x-gap="12" :y-gap="12" responsive="screen">
      <n-grid-item v-for="img in images" :key="img.filename">
        <n-card size="small">
          <template #header>{{ img.filename }}</template>
          <template #header-extra>
            <n-button text type="error" size="tiny" @click="delImage(img.filename)">删除</n-button>
          </template>
          <n-image
            width="100%"
            :src="`/uploads/${img.filename}`"
            :alt="img.filename"
            style="aspect-ratio:1;object-fit:contain;background:#000"
          />
          <n-text depth="3">{{ (img.size_bytes / 1024).toFixed(1) }} KB</n-text>
        </n-card>
      </n-grid-item>
    </n-grid>

    <n-pagination
      v-model:page="page"
      :page-size="pageSize"
      :item-count="total"
      :on-update:page="() => load()"
      style="margin-top:16px;justify-content:center"
    />
  </div>
</template>
