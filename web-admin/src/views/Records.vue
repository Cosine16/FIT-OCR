<script setup lang="ts">
import { h, ref, onMounted } from 'vue'
import { NButton, useMessage } from 'naive-ui'
import api from '@/api'

const message = useMessage()
const loading = ref(false)
const records = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const checkedIds = ref<Set<number>>(new Set())
const filterEngine = ref<string | null>(null)
const filterStatus = ref<string | null>(null)
const resultModal = ref(false)
const resultContent = ref('')
const resultFilename = ref('')

const columns = [
  { type: 'selection' as any },
  { title: 'ID', key: 'id', width: 60 },
  { title: '图片', key: 'image_filename', ellipsis: { tooltip: true }, width: 240 },
  { title: '引擎', key: 'engine', width: 140 },
  { title: '状态', key: 'status', width: 80,
    render: (row: any) => row.status === 'success'
      ? '✅' : '❌'
  },
  { title: '耗时(ms)', key: 'elapsed_ms', width: 100 },
  { title: '大小(KB)', key: 'image_size_bytes', width: 100,
    render: (row: any) => (row.image_size_bytes / 1024).toFixed(0)
  },
  { title: '时间', key: 'created_at', width: 170,
    render: (row: any) => new Date(row.created_at).toLocaleString('zh-CN')
  },
  { title: '操作', key: 'actions', width: 160,
    render: (row: any) => [
      h('span', { style: 'display:flex;gap:8px' }, [
        h(NButton, { size: 'tiny', onClick: () => viewResult(row) }, '查看结果'),
        h(NButton, { size: 'tiny', type: 'error', onClick: () => delRecord(row.id) }, '删除'),
      ])
    ]
  },
]

async function load() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize }
    if (filterEngine.value) params.engine = filterEngine.value
    if (filterStatus.value) params.status = filterStatus.value
    const res = await api.get('/records', { params })
    records.value = res.data.items
    total.value = res.data.total
  } catch (e: any) {
    message.error('加载失败: ' + (e?.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}

async function delRecord(id: number) {
  await api.delete(`/records/${id}`)
  message.success('已删除')
  load()
}

async function batchDelete() {
  if (checkedIds.value.size === 0) return
  await api.post('/records/batch-delete', { ids: [...checkedIds.value] })
  message.success(`已删除 ${checkedIds.value.size} 条`)
  checkedIds.value = new Set()
  load()
}

async function viewResult(row: any) {
  if (row.result_path) {
    const name = row.result_path.split('/').pop()
    const res = await api.get(`/results/${name}`)
    resultContent.value = res.data.content
    resultFilename.value = name
    resultModal.value = true
  }
}

function handleCheck(rowKeys: number[]) {
  checkedIds.value = new Set(rowKeys)
}

onMounted(load)
</script>

<template>
  <div>
    <h2 style="margin-top:0">识别记录</h2>

    <n-space style="margin-bottom:16px" align="center">
      <n-select
        v-model:value="filterEngine"
        :options="[
          { label: '全部引擎', value: null },
          { label: 'pix2text-local', value: 'pix2text-local' },
          { label: 'glm-4v-cloud', value: 'glm-4v-cloud' },
          { label: 'fallback(local→cloud)', value: 'fallback(local→cloud)' },
        ]"
        style="width:200px"
        @update:value="load"
      />
      <n-select
        v-model:value="filterStatus"
        :options="[
          { label: '全部状态', value: null },
          { label: '成功', value: 'success' },
          { label: '失败', value: 'failure' },
        ]"
        style="width:140px"
        @update:value="load"
      />
      <n-button type="error" secondary :disabled="checkedIds.size===0" @click="batchDelete">
        批量删除 ({{ checkedIds.size }})
      </n-button>
    </n-space>

    <n-data-table
      :columns="columns"
      :data="records"
      :loading="loading"
      :row-key="(row: any) => row.id"
      :checked-row-keys="[...checkedIds]"
      @update:checked-row-keys="handleCheck"
      :pagination="{
        page: page,
        pageSize: pageSize,
        itemCount: total,
        onChange: (p: number) => { page = p; load() },
        showSizePicker: false,
      }"
      size="small"
      max-height="calc(100vh - 240px)"
    />

    <n-modal v-model:show="resultModal" title="识别结果">
      <n-card style="width:700px;max-width:90vw">
        <pre style="max-height:60vh;overflow:auto;white-space:pre-wrap;font-size:13px">{{ resultContent }}</pre>
      </n-card>
    </n-modal>
  </div>
</template>
