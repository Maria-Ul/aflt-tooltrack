import { StyleSheet, Text, View } from 'react-native'
import React, { useState } from 'react'
import { Button, ButtonText, Card, Center, Heading, HStack, Input, InputField, ScrollView, VStack } from '@gluestack-ui/themed'
import { createAircraftRequest } from '../../../../api/new/aircraft/create_aircraft'
import { AIRCRAFT_LIST_ROUTE } from '../../Screens'

const AircraftCreateScreen = ({ navigation }) => {
    var [tail_number, setTailNumber] = useState("")
    var [model, setModel] = useState("")
    var [year_of_manufacture, setYearOfManufacture] = useState("")
    var [description, setDescription] = useState("")

    var isAddEnabled = tail_number.length > 0 && model.length > 0 &&
        year_of_manufacture.length == 4 && year_of_manufacture > 1930 && year_of_manufacture < 2026

    const onAddClick = () => {
        console.log("ADD")
        createAircraftRequest({
            tail_number,
            model,
            year_of_manufacture,
            description,
            onSuccess: ({ data }) => {
                navigation.goBack()
            }
        })
    }

    const onBackClick = () => {
        navigation.goBack()
    }

    return (
        <Center>
            <Card m="$10">
                <VStack space="md" p="$5">
                    <Heading>Добавить воздушное судно</Heading>
                    <Text>Бортовой номер</Text>
                    <Input>
                        <InputField value={tail_number} onChangeText={setTailNumber} placeholder="Номер" />
                    </Input>
                    <Text>Модель</Text>
                    <Input>
                        <InputField value={model} onChangeText={setModel} placeholder="Модель воздушного судна" />
                    </Input>
                    <Text>Год производства</Text>
                    <Input >
                        <InputField inputMode='decimal'
                            value={year_of_manufacture}
                            onChangeText={setYearOfManufacture}
                            placeholder="Год" />
                    </Input>
                    <Text>Описание</Text>
                    <Input>
                        <InputField value={description} onChangeText={setDescription} placeholder="Описание" />
                    </Input>
                    <HStack space="md">
                        <Button onPress={onAddClick} disabled={!isAddEnabled}>
                            <ButtonText>Добавить</ButtonText>
                        </Button>
                        <Button variant='outline' onPress={onBackClick}>
                            <ButtonText>Отмена</ButtonText>
                        </Button>
                    </HStack>
                </VStack>
            </Card>
        </Center>
    )
}

export default AircraftCreateScreen

const styles = StyleSheet.create({})