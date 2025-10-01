import AsyncStorage from "@react-native-async-storage/async-storage"
import { afltToolscanApi } from "../../baseApi"
import { SESSION_TOKEN } from "../login"

export const getToolkitWithTools = async ({
    id,
    onSuccess
}) => {
    const sessionToken = await AsyncStorage.getItem(SESSION_TOKEN)
    var response = await afltToolscanApi.get(
        url = `/api/tool-sets/${id}/with-tools`,
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
        console.log(response)
    }
}