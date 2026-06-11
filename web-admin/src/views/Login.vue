<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function doLogin() {
  loading.value = true
  error.value = ''
  try {
    const res = await api.post('/login', {
      username: username.value,
      password: password.value,
    })
    localStorage.setItem('token', res.data.access_token)
    router.push('/')
  } catch (_e) {
    error.value = '用户名或密码错误'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <n-card class="login-card" title="FIT-OCR 管理后台">
      <n-form>
        <n-form-item label="用户名">
          <n-input v-model:value="username" placeholder="admin" @keyup.enter="doLogin" />
        </n-form-item>
        <n-form-item label="密码">
          <n-input v-model:value="password" type="password" placeholder="••••••" @keyup.enter="doLogin" />
        </n-form-item>
        <n-button type="primary" block :loading="loading" @click="doLogin">登 录</n-button>
        <n-alert v-if="error" type="error" style="margin-top: 12px">{{ error }}</n-alert>
      </n-form>
    </n-card>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #101014;
}
.login-card {
  width: 380px;
  max-width: 90vw;
}
</style>
