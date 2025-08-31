<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8" lg="6">
        <v-card class="pa-4" elevation="2">
          <v-card-title class="text-h5 text-center">
            Telegram Session 生成器
          </v-card-title>
          <v-card-subtitle class="text-center">
            安全地在您的浏览器中生成 Telethon Session
          </v-card-subtitle>
          
          <v-divider class="my-4"></v-divider>

          <v-form @submit.prevent="startGeneration">
            <!-- API Credentials -->
            <div v-if="step === 'initial'">
              <v-text-field
                v-model="credentials.api_id"
                label="API ID"
                placeholder="请输入您的 API ID"
                required
                type="number"
                variant="outlined"
              ></v-text-field>
              <v-text-field
                v-model="credentials.api_hash"
                label="API Hash"
                placeholder="请输入您的 API Hash"
                required
                variant="outlined"
              ></v-text-field>
              
            </div>

            <!-- Dynamic Steps -->
            <v-text-field
              v-if="step === 'phone'"
              v-model="inputs.phone"
              label="手机号码"
              placeholder="例如：+8612345678900"
              variant="outlined"
            ></v-text-field>
            <v-text-field
              v-if="step === 'code'"
              v-model="inputs.code"
              label="验证码"
              placeholder="请输入您收到的验证码"
              variant="outlined"
            ></v-text-field>
            <v-text-field
              v-if="step === 'password'"
              v-model="inputs.password"
              label="两步验证密码"
              type="password"
              placeholder="如果您设置了，请输入密码"
              variant="outlined"
            ></v-text-field>

            <!-- Results -->
            <v-textarea
              v-if="sessionString"
              v-model="sessionString"
              label="您的 Session String"
              readonly
              auto-grow
              variant="outlined"
              rows="3"
            >
              <template v-slot:append-inner>
                <v-btn icon="mdi-content-copy" variant="text" @click="copyToClipboard"></v-btn>
              </template>
            </v-textarea>

            <v-alert
              v-if="error"
              type="error"
              variant="tonal"
              class="mb-4"
              :text="error"
            ></v-alert>

            <v-btn 
              :loading="loading" 
              :disabled="loading || !!sessionString"
              type="submit" 
              color="primary" 
              block 
              size="large"
            >
              {{ buttonText }}
            </v-btn>
          </v-form>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import { createWebSocket } from '@/api';

const step = ref('initial'); // initial, phone, code, password, done
const loading = ref(false);
const error = ref('');
const sessionString = ref('');

const credentials = reactive({
  api_id: '',
  api_hash: '',
});


const inputs = reactive({
  phone: '',
  code: '',
  password: '',
});

let socket: WebSocket | null = null;

const buttonText = computed(() => {
  if (loading.value) return '正在处理...';
  if (step.value === 'initial') return '开始生成';
  if (step.value === 'phone') return '发送手机号码';
  if (step.value === 'code') return '提交验证码';
  if (step.value === 'password') return '提交密码';
  if (sessionString.value) return '已完成';
  return '开始';
});

function startGeneration() {
  if (step.value === 'initial') {
    loading.value = true;
    error.value = '';
    
    socket = createWebSocket('/tg/ws/generate_session');

    socket.onopen = () => {
      const initialData = {
        api_id: parseInt(credentials.api_id),
        api_hash: credentials.api_hash,
      };
      send('start', initialData);
    };

    socket.onmessage = (event) => {
      loading.value = false;
      const message = JSON.parse(event.data);

      switch (message.status) {
        case 'waiting_for_phone':
          step.value = 'phone';
          break;
        case 'waiting_for_code':
          step.value = 'code';
          break;
        case 'waiting_for_password':
          step.value = 'password';
          break;
        case 'success':
          sessionString.value = message.data;
          step.value = 'done';
          socket?.close();
          break;
        case 'error':
          error.value = message.data;
          step.value = 'initial';
          socket?.close();
          break;
      }
    };

    socket.onerror = () => {
      error.value = '无法连接到 WebSocket 服务器。请确保后端服务正在运行。';
      loading.value = false;
    };
    
    socket.onclose = () => {
      loading.value = false;
    };
  } else {
    const currentStep = step.value;
    const data = inputs[currentStep as keyof typeof inputs];
    if (data) {
      loading.value = true;
      send(currentStep, data);
    }
  }
}

function send(type: string, data: any) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ type, data }));
  }
}

async function copyToClipboard() {
  try {
    await navigator.clipboard.writeText(sessionString.value);
    // 可以在这里加一个提示，例如 snackbar
  } catch (err) {
    error.value = '复制失败';
  }
}
</script>

<style scoped>
.v-card {
  border-radius: 12px;
}
</style>