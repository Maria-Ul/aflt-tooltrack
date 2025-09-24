import axios from "axios";

export const BACKEND_URL = "http://localhost:8000"
export const afltToolscanApi = axios.create(
    {
        baseURL: BACKEND_URL,
    }
)