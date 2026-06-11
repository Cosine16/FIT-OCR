<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api'

interface Overview {
  total_calls: number
  success_count: number
  failure_count: number
  avg_elapsed_ms: number
}

interface EngineStat {
  engine: string
  count: number
  pct: number
}

const overview = ref<Overview | null>(null)
const engines = ref<EngineStat[]>([])

onMounted(async () => {
  const [ov, en] = await Promise.all([
    api.get('/stats/overview'),
    api.get('/stats/engines'),
  ])
  overview.value = ov.data
  engines.value = en.data
})
</script>

<template>
  <div>
    <h2 style="margin-top:0">仪表盘</h2>
    <n-grid :cols="4" :x-gap="16" :y-gap="16" responsive="screen">
      <n-grid-item>
        <n-card>
          <n-statistic label="总调用次数" :value="overview?.total_calls ?? 0" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="成功" :value="overview?.success_count ?? 0" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="失败" :value="overview?.failure_count ?? 0" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="平均耗时(ms)" :value="overview?.avg_elapsed_ms ?? 0" />
        </n-card>
      </n-grid-item>
    </n-grid>

    <n-card title="引擎占比" style="margin-top: 16px">
      <n-data-table
        :columns="[
          { title: '引擎', key: 'engine' },
          { title: '调用次数', key: 'count' },
          { title: '占比', key: 'pct', render: (row: any) => `${row.pct}%` },
        ]"
        :data="engines"
        :bordered="false"
        size="small"
      />
    </n-card>
  </div>
</template>
