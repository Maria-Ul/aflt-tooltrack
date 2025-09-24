import AsyncStorage from "@react-native-async-storage/async-storage"
import { afltToolscanApi } from "../baseApi"

export const SESSION_TOKEN = "sessionToken"
export const loginRequest = async ({username, password, onSuccess, onError}) => {
    var response = await afltToolscanApi.post(
        url = "/login",
        data = {
            tab_number: username,
            password: password,
        },
    )
    if (response.status == 200) {
        AsyncStorage.setItem(SESSION_TOKEN, response.data.access_token)
        console.log(response)
        onSuccess()
    } else {
       console.log(response)
    }
}