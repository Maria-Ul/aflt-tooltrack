import AsyncStorage from "@react-native-async-storage/async-storage"
import { generateImageApi } from "./baseApi"
import { SESSION_TOKEN } from "./login"

export const registerReguset = async ({username, password, onSuccess}) => {
    var response = await generateImageApi.post(
        url = "/register",
        data = {
            username: username,
            password: password,
        }
    )
    if (response.status == 201) {
        AsyncStorage.setItem(SESSION_TOKEN, response.data.token)
        console.log(response)
        onSuccess()
    } else {
        console.log(response)
    }
}