import { Button, ButtonText, Card, Center, Heading, Input, InputField, Text, VStack } from "@gluestack-ui/themed"
import { useState } from "react";
import { register, registerReguset } from "../api/register";

const RegistrationScreen = ({ navigation }) => {
    const [password, setPassword] = useState("")
    const [passwordRepeat, setPasswordRepeat] = useState("")
    const [login, setLogin] = useState("")
    let isNextEnabled = password == passwordRepeat

    const onRegistration = () => {
        registerReguset({
            username: login, password: password, onSuccess: () => {
                navigation.replace("ImageGenerator")
            }
        })
    }
    const onBack = () => {
        navigation.goBack()
        //navigation.replace("Auth")
    }
    return (
        <Center p="$10">
            <Card>
                <VStack space="md">
                    <Heading>Регистрация</Heading>
                    <Text>Логин</Text>
                    <Input>
                        <InputField value={login} onChangeText={setLogin} placeholder="Логин" />
                    </Input>
                    <Text>Пароль</Text>
                    <Input>
                        <InputField value={password} onChangeText={setPassword} type="password" placeholder="Пароль" />
                    </Input>
                    <Input>
                        <InputField value={passwordRepeat} onChangeText={setPasswordRepeat} type="password" placeholder="Повторите пароль" />
                    </Input>
                    <Button onPress={onRegistration} isDisabled={!isNextEnabled}>
                        <ButtonText>Зарегистрироваться</ButtonText>
                    </Button>
                    <Button onPress={onBack} variant="outline">
                        <ButtonText>Назад</ButtonText>
                    </Button>
                </VStack>
            </Card>
        </Center>
    )
}
export default RegistrationScreen;