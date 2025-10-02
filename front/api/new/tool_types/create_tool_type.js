import AsyncStorage from "@react-native-async-storage/async-storage"
import { afltToolscanApi } from "../../baseApi"
import { SESSION_TOKEN } from "../login"

export const createToolTypeRequest = async ({
    name,
    category_id,
    is_item,
    type_class,
    onSuccess
}) => {
    const sessionToken = await AsyncStorage.getItem(SESSION_TOKEN)
    console.log("CREATE_TOOL_TYPES", type_class)
    var response = await afltToolscanApi.post(
        url = "/api/tool-types/",
        data = {
            name: name,
            category_id: category_id,
            is_item: is_item,
            tool_class: type_class,
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