import { Button, ButtonText, Card, Center, CircleIcon, Heading, HStack, Input, InputField, Radio, RadioGroup, RadioIcon, RadioIndicator, RadioLabel, Text, VStack } from "@gluestack-ui/themed"
import { useState } from "react";
import { ADMIN_ROLE, QA_EMPLOYEE_ROLE, register, registerReguset, WAREHOUSE_EMPLOYEE_ROLE, WORKER_ROLE, WORKERS_PIPELINE_ROLE } from "../../api/new/register";

const RegistrationScreen = ({ navigation }) => {
    const [password, setPassword] = useState("")
    const [passwordRepeat, setPasswordRepeat] = useState("")
    const [name, setName] = useState("")
    const [surname, setSurname] = useState("")
    const [patronymic, setPatronymic] = useState("")
    const [employeeNumber, setEmployeeNumber] = useState("")
    const [role, setRole] = useState(WORKER_ROLE)
    let isNextEnabled = password == passwordRepeat && password != ""
        && employeeNumber != "" && name != ""

    const onRegistration = () => {
        registerReguset({
            employeeNumber: employeeNumber,
            name: name,
            surname: surname,
            patronymic: patronymic,
            password: password,
            role: role,
            onSuccess: () => {
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
                        <InputField value={employeeNumber} onChangeText={setEmployeeNumber} placeholder="Табельный номер" />
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

                    <Text>Роль</Text>
                    <RadioGroup value={role} onChange={setRole}>
                        <HStack space="sm">
                            <Radio value={WAREHOUSE_EMPLOYEE_ROLE}>
                                <RadioIndicator mr='$2'>
                                    <RadioIcon as={CircleIcon} />
                                </RadioIndicator>
                                <RadioLabel>Сотрудник склада</RadioLabel>
                            </Radio>
                            <Radio value={WORKER_ROLE}>
                                <RadioIndicator mr='$2'>
                                    <RadioIcon as={CircleIcon} />
                                </RadioIndicator>
                                <RadioLabel>Авиаинженер</RadioLabel>
                            </Radio>
                            <Radio value={QA_EMPLOYEE_ROLE}>
                                <RadioIndicator mr='$2'>
                                    <RadioIcon as={CircleIcon} />
                                </RadioIndicator>
                                <RadioLabel>Специалист службы качества</RadioLabel>
                            </Radio>
                            <Radio value={WORKERS_PIPELINE_ROLE}>
                                <RadioIndicator mr='$2'>
                                    <RadioIcon as={CircleIcon} />
                                </RadioIndicator>
                                <RadioLabel>Техническая роль (выдача/прием)</RadioLabel>
                            </Radio>
                        </HStack>
                    </RadioGroup>

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