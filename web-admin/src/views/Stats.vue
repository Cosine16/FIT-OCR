<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import api from '@/api'

interface TrendPoint { date: string; count: number }
interface EngineStat { engine: string; count: number; pct: number }

const message = useMessage()
const trendDays = ref(7)
const trend = ref<TrendPoint[]>([])
const engines = ref<EngineStat[]>([])

async function loadTrend() {
  try {
    const res = await api.get('/stats/trend', { params: { days: trendDays.value } })
    trend.value = res.data
  } catch (e: any) {
    message.error('加载失败')
  }
}

async function loadEngines() {
  const res = await api.get('/stats/engines')
  engines.value = res.data
}

onMounted(() => {
  loadTrend()
  loadEngines()
})
</script>

<template>
  <div>
    <h2 style="margin-top:0">调用统计</h2>

    <n-grid :cols="2" :x-gap="16">
      <n-grid-item>
        <n-card title="每日调用量">
          <template #header-extra>
            <n-select
              v-model:value="trendDays"
              :options="[
                { label: '近7天', value: 7 },
                { label: '近30天', value: 30 },
              ]"
              size="small"
              style="width:100px"
              @update:value="loadTrend"
            />
          </template>
          <n-empty v-if="trend.length === 0" description="暂无数据" />
          <n-data-table
            v-else
            :columns="[
              { title: '日期', key: 'date' },
              { title: '调用量', key: 'count' },
            ]"
            :data="trend"
            size="small"
          />
        </n-card>
      </n-grid-item>

      <n-grid-item>
        <n-card title="引擎分布">
          <n-empty v-if="engines.length === 0" description="暂无数据" />
          <n-data-table
            v-else
            :columns="[
              { title: '引擎', key: 'engine' },
              { title: '调用次数', key: 'count' },
              { title: '占比', key: 'pct', render: (row: any) => `${row.pct}%` },
            ]"
            :data="engines"
            size="small"
          />
        </n-card>
      </n-grid-item>
    </n-grid>
  </div>
</template>
