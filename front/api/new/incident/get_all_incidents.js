import AsyncStorage from "@react-native-async-storage/async-storage"
import { afltToolscanApi } from "../../baseApi"
import { SESSION_TOKEN } from "../login"

export const getAllIncidentsRequest = async ({ onSuccess }) => {
    const sessionToken = await AsyncStorage.getItem(SESSION_TOKEN)
    var response = await afltToolscanApi.get(
        url = "/api/incidents/",
        config = {
            headers: {
                Authorization: "Bearer " + sessionToken
            },
            params: {
                skip: 0,
                limit: 1000,
            }
        }
    )
    if (response.status == 200) {
        onSuccess(response.data)
        console.log(response)
    } else {
        console.log(response)
    }
}