import AsyncStorage from "@react-native-async-storage/async-storage"
import { afltToolscanApi, BACKEND_URL } from "../../baseApi"
import { SESSION_TOKEN } from "../login"
import { Platform } from "react-native";

export const saveZipSimple = async (response) => {
  if (Platform.OS === 'web') {
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'prediction.zip';
    a.click();
    window.URL.revokeObjectURL(url);
    
  }
};


export const sendImageToPredictRequest = async ({
    file,
    onSuccess
}) => {
    const sessionToken = await AsyncStorage.getItem(SESSION_TOKEN)

    const formData = new FormData();
    fetch(file.uri)
        .then(res => res.blob())
        .then(blob => {
            const fileWithName = new File([blob], file.name, {
                type: blob.type || 'image/jpeg'
            });
            formData.append('file', fileWithName)
            fetch(BACKEND_URL + "/api/files/predict/single", {
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