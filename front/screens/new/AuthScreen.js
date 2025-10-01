import { Button, ButtonText, Card, Center, Heading, Input, InputField, ScrollView, Text, VStack } from "@gluestack-ui/themed"
import { useEffect, useState } from "react"
import { SESSION_TOKEN, loginRequest } from "../../api/new/login"
import AsyncStorage from "@react-native-async-storage/async-storage"
import { EMPLOYEE_NUMBER_ROUTE, QA_EMPLOYEE_ROLE_ROUTE, REGISTRATION_SCREEN_ROUTE, TOOLS_SCANNER_ROUTE, WAREHOUSE_EMPLOYEE_ROUTE, WORKERS_PIPELINE_ROLE_ROUTE } from "./Screens"
import { ADMIN_ROLE, QA_EMPLOYEE_ROLE, WAREHOUSE_EMPLOYEE_ROLE, WORKER_ROLE, WORKERS_PIPELINE_ROLE } from "../../api/new/register"
import { getDocumentAsync } from "expo-document-picker"
import { sendImageToPredictRequest } from "../../api/new/send_image/send_image_to_predict"
import { sendZipToPredictRequest } from "../../api/new/send_image/send_zip_to_predict"

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
        //navigation.replace(WORKERS_PIPELINE_ROLE_ROUTE)
        //navigation.replace(WAREHOUSE_EMPLOYEE_ROUTE)
        loginRequest({
            username: login, password: password, onSuccess: ({ resRole }) => {
                switch (resRole) {
                    case WORKER_ROLE: navigation.replace(WORKERS_PIPELINE_ROLE_ROUTE); break
                    case ADMIN_ROLE: navigation.replace(ADMIN_ROLE); break
                    case WAREHOUSE_EMPLOYEE_ROLE: navigation.replace(WAREHOUSE_EMPLOYEE_ROUTE); break
                    case QA_EMPLOYEE_ROLE: navigation.replace(QA_EMPLOYEE_ROLE_ROUTE); break
                    case WORKERS_PIPELINE_ROLE: navigation.replace(WORKERS_PIPELINE_ROLE_ROUTE); break
                }
            }
        })
    }
    const [login, setLogin] = useState("")
    const [password, setPassword] = useState("")


    const onUploadPhotoClick = async () => {
        var result = await getDocumentAsync({ type: ["image/jpeg", "image/png"] })
        if (result.assets.length > 0) {
            sendImageToPredictRequest({
                file: result.assets[0],
                onSuccess: (data) => { }
            })
        }
    }

    const onUploadZipClick = async () => {
        var result = await getDocumentAsync({ type: 'application/zip' })
        if (result.assets.length > 0) {
            sendZipToPredictRequest({
                file: result.assets[0],
                onSuccess: (data) => { }
            })
        }
    }

    return (
        <ScrollView>
            <Center p="$10">
                <VStack space="md">
                    <Card>
                        <VStack space="md">
                            <Heading>Авторизация</Heading>
                            <Text>Логин</Text>
                            <Input>
                                <InputField
                                    inputMode="decimal"
                                    value={login}
                                    placeholder="Табельный номер" onChangeText={setLogin} />
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
                    <Card>
                        <VStack space='sm'>
                            <Heading>Быстрый тест без логина</Heading>
                            <Text>Загрузите фото или архив с несколькими фото.</Text>
                            <Text>{`Архив с результатами распознавания будет сохранен\nв Загрузки через пару секунд.`}</Text>
                            <Button variant='outline' onPress={onUploadPhotoClick}>
                                <ButtonText>Загрузить фото</ButtonText>
                            </Button>
                            <Button variant='outline' onPress={onUploadZipClick}>
                                <ButtonText>Загрузить архив</ButtonText>
                            </Button>
                        </VStack>
                    </Card>
                </VStack>
            </Center>
        </ScrollView>

    )
}
export default AuthScreen;