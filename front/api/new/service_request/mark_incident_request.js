import AsyncStorage from "@react-native-async-storage/async-storage"
import { afltToolscanApi } from "../../baseApi"
import { SESSION_TOKEN } from "../login"

export const markIncidentRequest = async ({
    request_id,
    comment,
    onSuccess,
    onError,
}) => {
    const sessionToken = await AsyncStorage.getItem(SESSION_TOKEN)
    try {
        var response = await afltToolscanApi.put(
            url = `/api/maintenance-requests/${request_id}/mark-incident`,
            data = {
                comments: comment,
            },
            config = {
                headers: {
                    Authorization: "Bearer " + sessionToken
                },
            }
        )
        if (response.status == 200) {
            onSuccess(response.data)
            console.log(response)
        } else {
            onError()
            console.log(response)
        }

    } catch {
        console.log("ERROR")
        onError()
    }
}