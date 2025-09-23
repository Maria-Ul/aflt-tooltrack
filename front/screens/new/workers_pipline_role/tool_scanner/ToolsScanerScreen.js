import { StyleSheet } from 'react-native'
import React, { useRef } from 'react'
import { CameraView, useCameraPermissions } from 'expo-camera'
import { Button, ButtonText, Center, Heading, HStack, VStack, Text, View } from '@gluestack-ui/themed'
import { Header } from '@rneui/themed'
import ToolItem from './ToolItem'
import WhiteCard from '../../../../components/WhiteCard'


// использовать Grid
const ToolsScanerScreen = ({ navigation }) => {
    const ref = useRef(null)

    const [permission, requestPermission] = useCameraPermissions()

    if (!permission) {
        // Camera permissions are still loading.
        return <View />;
    }

    if (!permission.granted) {
        // Camera permissions are not granted yet.
        return (
            <View style={styles.container} width='100%' height='100%'>
                <Center p='$10'>
                    <WhiteCard>
                        <VStack p='$5'>
                            <Text mb='$10' size='2xl' style={styles.message}>Необходимо разрешить доступ к камере</Text>
                            <Button onPress={requestPermission} title="grant permission">
                                <ButtonText>Разрешить</ButtonText>
                            </Button>
                        </VStack>
                    </WhiteCard>
                </Center>
            </View>
        );
    }


    return (
        <HStack style={styles.container}>
            <VStack style={styles.container_buttons} p='$1'>
                <Heading size='lg' m='$5'>Набор №12312312312</Heading>
                <WhiteCard>
                    <VStack p='$5' mb='$9'>
                        <Text size='lg' mb='$5'>Инструменты в наборе:</Text>

                        <ToolItem
                            name='Пассатижи'
                            probability={0.7}
                            threshold={0.98}
                        />
                        <ToolItem
                            name='Отвертка крестовая. PH4'
                            probability={0.99}
                            threshold={0.98}
                        />

                        <Button mb='$3'>
                            <ButtonText>Зафиксировать</ButtonText>
                        </Button>
                        <Button variant='outline'>
                            <ButtonText>Загрузить фото</ButtonText>
                        </Button>
                    </VStack>
                </WhiteCard>
            </VStack>
            <VStack style={styles.container_camera} p='$10'>
                <CameraView
                    ref={ref}
                    style={styles.camera}
                >asdfsadfmkasdkvnmsdfvnsjdnfvjndfjnv</CameraView>
            </VStack>
        </HStack>
    )
}

export default ToolsScanerScreen

const styles = StyleSheet.create({
    container: {
        flex: 100,
    },
    container_buttons: {
        flex: 30,
    },
    container_camera: {
        flex: 70,
    },
    camera: {
        flex: 80,
        'clip-path': 'inset(0% 0% 0% 0% round 20px)',
    }
})