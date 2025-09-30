import AsyncStorage from "@react-native-async-storage/async-storage"
import { afltToolscanApi } from "../../baseApi"
import { SESSION_TOKEN } from "../login"

export const deleteToolkitRequest = async ({
    toolkitId,
    onSuccess
}) => {
    const sessionToken = await AsyncStorage.getItem(SESSION_TOKEN)
    var response = await afltToolscanApi.delete(
        url = `/api/tool-sets/${toolkitId}`,
        {
            headers: {
                'Authorization': "Bearer " + sessionToken
            }
        },
    )
    if (response.status == 204) {
        onSuccess()
        console.log(response)
    } else {
        console.log(response)
    }
}