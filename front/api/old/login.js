import AsyncStorage from "@react-native-async-storage/async-storage"
import { generateImageApi } from "./baseApi"

export const SESSION_TOKEN = "sessionToken"
export const loginRequest = async ({username, password, onSuccess, onError}) => {
    var response = await generateImageApi.post(
        url = "/login",
        data = {
            username: username,
            password: password,
        },
    )
    if (response.status == 200) {
        AsyncStorage.setItem(SESSION_TOKEN, response.data.token)
        console.log(response)
        onSuccess()
    } else {
       console.log(response)
    }
}