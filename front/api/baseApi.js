import axios from "axios";

export const BACKEND_URL = "http://185.44.167.225:8000"
export const WEB_SOCKET_URL = "ws://185.44.167.225:8000"
export const afltToolscanApi = axios.create(
    {
        baseURL: BACKEND_URL,
    }
)