import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';
import { SESSION_TOKEN } from './login';
import { BACKEND_URL, generateImageApi } from './baseApi';

export const getImageRequest = async ({ imageName, onSuccess }) => {
    const sessionToken = await AsyncStorage.getItem(SESSION_TOKEN)
    var response = await generateImageApi.get(
        url = `/image/${imageName}`,
        config = {
            headers: {
                Authorization: "Bearer " + sessionToken,
                //responseType: "arraybuffer",
            }
        }
    )
    //const headers = new Headers();
    //headers.set('Authorization', `Bearer ${sessionToken}`);
    //const response = await fetch(BACKEND_URL+`/image/${imageName}`, { headers });
    if (response.status == 200) {
        //var binaryData = await response.blob()
        //const objectUrl = URL.createObjectURL(blob);

        //var base64 = btoa(String.fromCharCode(...new Uint8Array(binaryData)))

        var Buffer = require('buffer/').Buffer
        let base64 = Buffer.from(response.data).toString('base64');
        const result = `data:image/png;base64, ${base64}`
        onSuccess(result)
        //console.log(base64)
    } else {
        console.log(response)
    }
}