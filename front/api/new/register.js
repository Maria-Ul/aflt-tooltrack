import AsyncStorage from "@react-native-async-storage/async-storage"
import { afltToolscanApi } from "../baseApi"
import { SESSION_TOKEN } from "./login"

export const ADMIN_ROLE = "administrator"
export const WAREHOUSE_EMPLOYEE_ROLE = "warehouse_employee"
export const WORKER_ROLE = "aviation_engineer"
export const WORKERS_PIPELINE_ROLE = "conveyor"
export const QA_EMPLOYEE_ROLE = "quality_control_specialist"

export const registerReguset = async ({
    employeeNumber,
    name,
    surname,
    patronymic,
    role,
    password,
    onSuccess
}) => {
    var response = await afltToolscanApi.post(
        url = "/api/auth/register",
        data = {
            tab_number: employeeNumber,
            full_name: surname + " " + name + " " + patronymic,
            role: role,
            password: password,
        }
    )
    if (response.status == 201) {
        AsyncStorage.setItem(SESSION_TOKEN, response.data.access_token)
        console.log(response)
        onSuccess({ resRole: response.data.role })
    } else {
        console.log(response)
    }
}