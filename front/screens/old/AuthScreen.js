import { Button, ButtonText, Card, Center, Heading, Input, InputField, Text, VStack } from "@gluestack-ui/themed"
import { useEffect, useState } from "react"
import { SESSION_TOKEN, loginRequest } from "../api/login"
import AsyncStorage from "@react-native-async-storage/async-storage"

const AuthScreen = ({ navigation }) => {
    useEffect(() => {
        const checkSession = async () => {
            const sessionToken = await AsyncStorage.getItem(SESSION_TOKEN)
            if (sessionToken.length > 0) {
                navigation.replace("ImageGenerator")
            }
        }
        checkSession()
    }, [])
    const onRegistration = () => {
        navigation.navigate("Registration")
    }
    const onLogin = () => {
        loginRequest({
            username: login, password: password, onSuccess: () => {
                navigation.replace("ImageGenerator")
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
                        <InputField value={login} placeholder="Логин" onChangeText={setLogin} />
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