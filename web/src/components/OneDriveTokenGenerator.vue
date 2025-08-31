<template>
  <v-card class="mx-auto" max-width="600">
    <v-card-title class="headline">
      OneDrive 刷新令牌生成器
    </v-card-title>
    <v-card-text>
      <p>输入您的 OneDrive 应用的客户端 ID 和密钥，然后点击下面的按钮以通过 OAuth 2.0 授权流程获取刷新令牌。</p>
      <v-text-field
        v-model="clientId"
        label="客户端 ID (Client ID)"
        class="mt-4"
        dense
        outlined
      ></v-text-field>
      <v-text-field
        v-model="clientSecret"
        label="客户端密钥 (Client Secret)"
        type="password"
        class="mt-2"
        dense
        outlined
      ></v-text-field>

      <v-alert v-if="authUrl" type="info" class="mt-4" dense>
        请在新标签页中打开以下链接完成授权：<br>
        <a :href="authUrl" target="_blank" rel="noopener noreferrer">{{ authUrl }}</a>
      </v-alert>

      <v-alert v-if="refreshToken" type="success" class="mt-4" dense>
        <strong>成功！</strong> 你的刷新令牌是：<br>
        <code class="pa-2 d-block" style="word-break: break-all;">{{ refreshToken }}</code>
      </v-alert>

      <v-alert v-if="error" type="error" class="mt-4" dense>
        {{ error }}
      </v-alert>
    </v-card-text>
    <v-card-actions>
      <v-btn color="primary" @click="startAuth" :disabled="loading">
        {{ loading ? '等待中...' : '开始授权' }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { createWebSocket } from '@/api';

const loading = ref(false);
const authUrl = ref('');
const refreshToken = ref('');
const error = ref('');
const clientId = ref('');
const clientSecret = ref('');
const ws = ref<WebSocket | null>(null);

const startAuth = () => {
  if (!clientId.value || !clientSecret.value) {
    error.value = '请输入客户端 ID 和客户端密钥。';
    return;
  }

  loading.value = true;
  error.value = '';
  authUrl.value = '';
  refreshToken.value = '';
  
  ws.value = createWebSocket('/ws/onedrive_token');

  ws.value.onopen = () => {
    console.log('WebSocket 连接已建立');
    ws.value?.send(JSON.stringify({
      type: 'start',
      data: {
        client_id: clientId.value,
        client_secret: clientSecret.value
      }
    }));
  };

  ws.value.onmessage = (event) => {
    const message = JSON.parse(event.data);
    
    switch (message.status) {
      case 'waiting_for_auth':
        authUrl.value = message.data;
        break;
      case 'success':
        refreshToken.value = message.data;
        loading.value = false;
        ws.value?.close();
        break;
      case 'error':
        error.value = `错误: ${message.data}`;
        loading.value = false;
        ws.value?.close();
        break;
    }
  };

  ws.value.onerror = (err) => {
    console.error('WebSocket 错误:', err);
    error.value = '无法连接到服务器。请确保后端服务正在运行。';
    loading.value = false;
  };

  ws.value.onclose = () => {
    console.log('WebSocket 连接已关闭');
    loading.value = false;
  };
};
</script>