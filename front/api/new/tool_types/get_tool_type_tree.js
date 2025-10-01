import AsyncStorage from "@react-native-async-storage/async-storage"
import { afltToolscanApi } from "../../baseApi"
import { SESSION_TOKEN } from "../login"

const mock = [
    {
        "name": "Отвертка",
        "category_id": null,
        "is_item": false,
        "id": 1,
        "children": [
            {
                "name": "Крестовая отвертка",
                "category_id": 1,
                "is_item": false,
                "id": 2,
                "children": [
                    {
                        "name": "Крестовая отвертка PH4",
                        "category_id": 2,
                        "is_item": true,
                        "id": 3,
                        "children": [],
                        "category": null
                    },
                ],
                "category": null
            },
        ],
        "category": null
    },
    {
        "name": "Плоскогубцы",
        "category_id": null,
        "is_item": false,
        "id": 4,
        "children": [
            {
                "name": "Плоскогубцы. Крутые",
                "category_id": 4,
                "is_item": false,
                "id": 5,
                "children": [],
                "category": null
            },
        ],
        "category": null
    },
]

export const getToolTypeTree = async ({ onSuccess }) => {
    const sessionToken = await AsyncStorage.getItem(SESSION_TOKEN)
    var response = await afltToolscanApi.get(
        url = "/api/tool-types/tree/root",
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