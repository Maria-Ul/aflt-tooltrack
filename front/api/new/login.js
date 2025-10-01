import AsyncStorage from "@react-native-async-storage/async-storage"
import { afltToolscanApi } from "../baseApi"
import { ADMIN_ROLE, QA_EMPLOYEE_ROLE, WAREHOUSE_EMPLOYEE_ROLE, WORKER_ROLE, WORKERS_PIPELINE_ROLE } from "./register"

export const SESSION_TOKEN = "sessionToken"
export const USER_NAME = "userName"
export const USER_ROLE = "userRole"

export const loginRequest = async ({ username, password, onSuccess, onError }) => {
    var response = await afltToolscanApi.post(
        url = "api/auth/login",
        data = {
            tab_number: username,
            password: password,
        },
    )
    if (response.status == 200) {
        await AsyncStorage.setItem(SESSION_TOKEN, response.data.access_token)
        await AsyncStorage.setItem(USER_NAME, response.data.full_name)
        await AsyncStorage.setItem(USER_ROLE, mapRole(response.data.role))

        console.log(response)
        onSuccess({ resRole: response.data.role })
    } else {
        console.log(response)
    }
}

const mapRole = (role) => {
    switch (role) {
        case QA_EMPLOYEE_ROLE: return "Специалист контроля качества"
        case WORKERS_PIPELINE_ROLE: return "Техническая роль (склад)"
        case WORKER_ROLE: return "Авиаинженер"
        case WAREHOUSE_EMPLOYEE_ROLE: return "Сотрудник склада"
        case ADMIN_ROLE: return "Администратор"
    }
}

