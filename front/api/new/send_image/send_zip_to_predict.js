import AsyncStorage from "@react-native-async-storage/async-storage"
import { afltToolscanApi, BACKEND_URL } from "../../baseApi"
import { SESSION_TOKEN } from "../login"
import * as FileSystem from 'expo-file-system';
import { Platform } from "react-native";
import { saveZipSimple } from "./send_image_to_predict";

export const sendZipToPredictRequest = async ({
    file,
    onSuccess
}) => {
    const sessionToken = await AsyncStorage.getItem(SESSION_TOKEN)
    const formData = new FormData();
    fetch(file.uri)
        .then(res => res.blob())
        .then(blob => {
            const fileWithName = new File([blob], file.name, {
                type: blob.type || 'application/zip'
            });
            formData.append('zip_file', fileWithName)
            fetch(BACKEND_URL + "/api/files/predict/batch", {
                method: 'post',
                body: formData
            }).then(zipResult => {
                saveZipSimple(zipResult)
            });
        })
    if (response.status == 201) {
        onSuccess(response.data)
        console.log(response)
    } else {
        console.log(response)
    }
}