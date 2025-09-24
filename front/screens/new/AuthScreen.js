import { Button, ButtonText, Card, Center, Heading, Input, InputField, Text, VStack } from "@gluestack-ui/themed"
import { useEffect, useState } from "react"
import { SESSION_TOKEN, loginRequest } from "../../api/new/login"
import AsyncStorage from "@react-native-async-storage/async-storage"
import { EMPLOYEE_NUMBER_ROUTE, REGISTRATION_SCREEN_ROUTE, TOOLS_SCANNER_ROUTE, WAREHOUSE_EMPLOYEE_ROUTE, WORKERS_PIPELINE_ROLE_ROUTE } from "./Screens"

const AuthScreen = ({ navigation }) => {
    useEffect(() => {
        const checkSession = async () => {
            const sessionToken = await AsyncStorage.getItem(SESSION_TOKEN)
            if (sessionToken.length > 0) {
                navigation.replace(EMPLOYEE_NUMBER_ROUTE)
            }
        }
        checkSession()
    }, [])
    const onRegistration = () => {
        navigation.navigate(REGISTRATION_SCREEN_ROUTE)
    }
    const onLogin = () => {
        navigation.replace(WORKERS_PIPELINE_ROLE_ROUTE)
        //navigation.replace(WAREHOUSE_EMPLOYEE_ROUTE)
        loginRequest({
            username: login, password: password, onSuccess: () => {
                navigation.replace(WORKERS_PIPELINE_ROLE_ROUTE)
            }
        })
    }
    const [login, setLogin] = useState("")
    const [password, setPassword] = useState("")
    return (
        <Center p="$10">
            <Card>
                <VStack space="md">
                    <Heading>Авторизация</Heading>
                    <Text>Логин</Text>
                    <Input>
                        <InputField value={login} placeholder="Табельный номер" onChangeText={setLogin} />
                    </Input>
                    <Text>Пароль</Text>
                    <Input>
                        <InputField value={password} type="password" placeholder="Пароль" onChangeText={setPassword} />
                    </Input>
                    <Button onPress={onLogin}>
                        <ButtonText>Войти</ButtonText>
                    </Button>
                    <Button variant="outline" onPress={onRegistration}>
                        <ButtonText>Регистрация</ButtonText>
                    </Button>
                </VStack>
            </Card>
        </Center>
    )
}
export default AuthScreen;