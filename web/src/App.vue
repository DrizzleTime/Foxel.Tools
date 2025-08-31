<template>
  <v-app>
    <v-app-bar app>
      <v-app-bar-title>Foxel 公共服务</v-app-bar-title>
      <v-spacer></v-spacer>
      <v-select
        v-model="selectedTool"
        :items="tools"
        item-title="name"
        item-value="component"
        label="选择工具"
        dense
        hide-details
        class="mx-4"
        style="max-width: 300px;"
      ></v-select>
      <v-spacer></v-spacer>
      <v-btn icon href="https://github.com/DrizzleTime/Foxel" target="_blank">
        <v-icon>mdi-github</v-icon>
      </v-btn>
    </v-app-bar>
    <v-main>
      <v-container>
        <component :is="selectedToolComponent" class="mt-4" />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import SessionGenerator from '@/components/SessionGenerator.vue';
import OneDriveTokenGenerator from '@/components/OneDriveTokenGenerator.vue';

const tools = [
  { name: 'Telegram Session 生成器', component: 'SessionGenerator' },
  { name: 'OneDrive 刷新令牌生成器', component: 'OneDriveTokenGenerator' },
];

const selectedTool = ref(tools[0].component);

const components = {
  SessionGenerator,
  OneDriveTokenGenerator,
};

const selectedToolComponent = computed(() => {
  return components[selectedTool.value as keyof typeof components];
});
</script>
