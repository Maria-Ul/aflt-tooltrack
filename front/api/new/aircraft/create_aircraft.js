
import AsyncStorage from "@react-native-async-storage/async-storage"
import { afltToolscanApi } from "../../baseApi"
import { SESSION_TOKEN } from "../login"

export const createAircraftRequest = async ({
    tail_number,
    model,
    year_of_manufacture,
    description,
    onSuccess
}) => {
    const sessionToken = await AsyncStorage.getItem(SESSION_TOKEN)
    var response = await afltToolscanApi.post(
        url = "/api/aircraft/",
        data = {
            tail_number: tail_number,
            model: model,
            year_of_manufacture: year_of_manufacture,
            description: description,
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