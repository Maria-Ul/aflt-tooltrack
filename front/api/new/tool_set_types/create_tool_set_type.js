import AsyncStorage from "@react-native-async-storage/async-storage"
import { afltToolscanApi } from "../../baseApi"
import { SESSION_TOKEN } from "../login"

export const createToolkitTypeRequest = async ({
    name,
    description,
    toolTypeIds,
    onSuccess
}) => {
    const sessionToken = await AsyncStorage.getItem(SESSION_TOKEN)
    var response = await afltToolscanApi.post(
        url = "/api/tool-set-types/",
        data = {
            name: name,
            description: description,
            tool_type_ids: toolTypeIds,
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