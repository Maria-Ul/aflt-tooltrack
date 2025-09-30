import AsyncStorage from "@react-native-async-storage/async-storage"
import { afltToolscanApi } from "../../baseApi"
import { SESSION_TOKEN } from "../login"

export const createToolkitRequest = async ({
    toolkitTypeId,
    batchNumber,
    description,
    toolsNumbersMap,
    onSuccess
}) => {
    const sessionToken = await AsyncStorage.getItem(SESSION_TOKEN)
    var response = await afltToolscanApi.post(
        url = "/api/tool-sets/",
        data = {
            tool_set_type_id: toolkitTypeId,
            batch_number: batchNumber,
            description: description,
            batch_map: toolsNumbersMap,
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