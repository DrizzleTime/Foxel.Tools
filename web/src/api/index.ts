import { ref } from 'vue';

const getWsBaseUrl = () => {
    if (import.meta.env.DEV) {
        return 'ws://127.0.0.1:8000/api';
    } else {
        return `/api`;
    }
}

export const baseUrl = ref(getWsBaseUrl());

export const createWebSocket = (path: string) => {
    const url = `${baseUrl.value}${path}`;
    return new WebSocket(url);
};