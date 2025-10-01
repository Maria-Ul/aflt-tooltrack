import axios from "axios";

export const BACKEND_URL = "http://localhost:8000"//"http://185.44.167.225"
export const afltToolscanApi = axios.create(
    {
        baseURL: BACKEND_URL,
    }
)