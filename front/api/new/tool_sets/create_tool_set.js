import AsyncStorage from "@react-native-async-storage/async-storage"
import { afltToolscanApi } from "../../baseApi"
import { SESSION_TOKEN } from "../login"

const mapToObj = m => {
    return Array.from(m).reduce((obj, [key, value]) => {
        obj[key] = value;
        return obj;
    }, {});
};

export const createToolkitRequest = async ({
    toolkitTypeId,
    batchNumber,
    description,
    toolsNumbersMap,
    onSuccess
}) => {
    const sessionToken = await AsyncStorage.getItem(SESSION_TOKEN)
    console.log("REQUEST", toolsNumbersMap)
    var response = await afltToolscanApi.post(
        url = "/api/tool-sets/",
        data = {
            tool_set_type_id: toolkitTypeId,
            batch_number: batchNumber,
            description: description,
            batch_map: mapToObj(toolsNumbersMap)
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