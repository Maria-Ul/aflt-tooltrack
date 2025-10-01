import AsyncStorage from "@react-native-async-storage/async-storage"
import { SESSION_TOKEN, USER_NAME, USER_ROLE } from "./login"

export const logout = () => {
    AsyncStorage.setItem(SESSION_TOKEN, "")
    AsyncStorage.setItem(USER_NAME, "")
    AsyncStorage.setItem(USER_ROLE, "")
} 