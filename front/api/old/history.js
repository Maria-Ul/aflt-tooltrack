import AsyncStorage from "@react-native-async-storage/async-storage"
import { generateImageApi } from "./baseApi"
import { SESSION_TOKEN } from "./login"

export const historyRequest = async({onSuccess}) => {
    const sessionToken = await AsyncStorage.getItem(SESSION_TOKEN)
    var response = await generateImageApi.get(
        url = "/history",
        config = {
            headers: {
                Authorization: "Bearer " + sessionToken
            }
        }
    )
    if (response.status == 200) {
        onSuccess(response.data)
        //console.log(response)
    } else {
        console.log(response)
    }
}