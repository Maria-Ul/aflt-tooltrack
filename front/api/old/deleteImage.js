import AsyncStorage from "@react-native-async-storage/async-storage"
import { generateImageApi } from "./baseApi"
import { SESSION_TOKEN } from "./login"

export const deleteImageRequest = async ({
    imageId, onSuccess,
}) => {
    const sessionToken = await AsyncStorage.getItem(SESSION_TOKEN)
    var response = await generateImageApi.delete(
        url = `/image/${imageId}`,
        {
            headers: {
                'Authorization': "Bearer " + sessionToken
            }
        },
    )
    if (response.status == 200) {
        onSuccess()
        console.log(response)
    } else {
        console.log(response)
    }
}