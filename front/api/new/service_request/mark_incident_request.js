import AsyncStorage from "@react-native-async-storage/async-storage"
import { afltToolscanApi } from "../../baseApi"
import { SESSION_TOKEN } from "../login"

export const markIncidentRequest = async ({
    request_id,
    onSuccess
}) => {
    const sessionToken = await AsyncStorage.getItem(SESSION_TOKEN)
    var response = await afltToolscanApi.put(
        url = `/api/maintenance-requests/${request_id}/mark-incident`,
        data = {
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
    if (response.status == 200) {
        onSuccess(response.data)
        console.log(response)
    } else {
        console.log(response)
    }
}