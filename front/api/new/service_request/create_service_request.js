import AsyncStorage from "@react-native-async-storage/async-storage"
import { afltToolscanApi } from "../../baseApi"
import { SESSION_TOKEN } from "../login"

export const createServiceRequest = async ({
    aircraft_id,
    warehouse_employee_id,
    aviation_engineer_id,
    tool_set_id,
    status,
    description,
    onSuccess
}) => {
    const sessionToken = await AsyncStorage.getItem(SESSION_TOKEN)
    var response = await afltToolscanApi.post(
        url = "/api/maintenance-requests/",
        data = {
            aircraft_id: aircraft_id,
            warehouse_employee_id: warehouse_employee_id,
            aviation_engineer_id: aviation_engineer_id,
            tool_set_id: tool_set_id,
            status: status,
            description: description,
        },
        {
            headers: {
                'Authorization': "Bearer " + sessionToken
            }
        },
    )
    if (response.status == 201) {
        onSuccess(response.data)
        console.log(response)
    } else {
        console.log(response)
    }
}