import { Button, ButtonText, Card, Center, Heading, Input, InputField, Text, VStack } from "@gluestack-ui/themed"
import { useState } from "react";
import { register, registerReguset } from "../../api/new/register";

const RegistrationScreen = ({ navigation }) => {
    const [password, setPassword] = useState("")
    const [passwordRepeat, setPasswordRepeat] = useState("")
    const [name, setName] = useState("")
    const [surname, setSurname] = useState("")
    const [patronymic, setPatronymic] = useState("")
    const [emplyeeNumber, setEmployeeNumber] = useState("")
    let isNextEnabled = password == passwordRepeat

    const onRegistration = () => {
        registerReguset({
            username: emplyeeNumber, password: password, onSuccess: () => {
                //navigation.replace("ImageGenerator")
            }
        })
    }
    const onBack = () => {
        navigation.goBack()
        navigation.replace("Auth")
    }
    return (
        <Center p="$10">
            <Card>
                <VStack space="md">
                    <Heading>Регистрация</Heading>
                    <Text>Табельный номер сотрудника</Text>
                    <Input>
                        <InputField value={emplyeeNumber} onChangeText={setEmployeeNumber} placeholder="Табельный номер" />
                    </Input>

                    <Text>ФИО</Text>
                    <Input>
                        <InputField value={name} onChangeText={setName} placeholder="Имя" />
                    </Input>
                    <Input>
                        <InputField value={surname} onChangeText={setSurname} placeholder="Фамилия" />
                    </Input>
                    <Input>
                        <InputField value={patronymic} onChangeText={setPatronymic} placeholder="Отчество" />
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