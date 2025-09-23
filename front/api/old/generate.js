import AsyncStorage from "@react-native-async-storage/async-storage"
import { generateImageApi } from "./baseApi"
import { SESSION_TOKEN } from "./login"

export const TASK_TYPE_IMAGE = "image"
export const TASK_TYPE_BANNER = "banner"
export const TASK_TYPE_INPAINT = "inpaint"

export const generateRequest = async ({
    taskType, taskData, onSuccess,
}) => {
    const sessionToken = await AsyncStorage.getItem(SESSION_TOKEN)
    var response = await generateImageApi.post(
        url = "/generate",
        data = {
            type: taskType,
            options: taskData,
        },
        {
            headers: {
                'Authorization': "Bearer " + sessionToken
            }
        },
    )
    if (response.status == 200) {
        onSuccess(response.data)
        console.log(response)
    } else {
        console.log(response)
    }
}
