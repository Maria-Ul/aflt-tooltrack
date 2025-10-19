import axios from "axios";

export const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_REST || "http://localhost:8000";
export const WEB_SOCKET_URL = process.env.EXPO_PUBLIC_BACKEND_WS || "ws://localhost:8000";

export const afltToolscanApi = axios.create(
    {
        baseURL: BACKEND_URL,
    }
)
