import { StyleSheet } from 'react-native'
import React from 'react'
import { Button, ButtonText, Card, Center, Heading, Icon, Text, VStack } from '@gluestack-ui/themed'
import { IdCardLanyardIcon } from 'lucide-react-native'
import { AUTH_SCREEN_ROUTE } from '../../Screens'

const AuthStageMenu = ({navigation}) => {

    const onPressToAuth = () => {
        navigation.replace(AUTH_SCREEN_ROUTE)
    }
    return (
        <Card variant='elevated' height="100%" justifyContent='center' alignItems='center'>
            <Center >
                <VStack space='sm' alignItems='center'>
                    <Icon size='xl' as={IdCardLanyardIcon} />
                    <Heading>Авторизация</Heading>
                    <Text textAlign='center'>Приложите пропуск для начала приема/выдачи инструментов</Text>
                    <Button onPress={onPressToAuth}>
                        <ButtonText>
                            К авторизации по логину
                        </ButtonText>
                    </Button>
                </VStack>
            </Center>
        </Card>
    )
}

export default AuthStageMenu

const styles = StyleSheet.create({})