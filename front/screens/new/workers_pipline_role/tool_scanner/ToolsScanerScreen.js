import { StyleSheet } from 'react-native'
import React, { useCallback, useEffect, useRef, useState } from 'react'
import { CameraView, useCameraPermissions } from 'expo-camera'
import { Button, ButtonText, Center, Heading, HStack, VStack, Text, View, Card, Box } from '@gluestack-ui/themed'
import { Header } from '@rneui/themed'
import ToolItem from './ToolItem'
import WhiteCard from '../../../../components/WhiteCard'
import ResultModal from './ResultModal'
import { BACKEND_URL } from '../../../../api/baseApi'
import { io } from 'socket.io-client'

// использовать Grid
const ToolsScanerScreen = ({ navigation }) => {
    const cameraRef = useRef(null)
    const socketRef = useRef(null)
    const streamIntervalRef = useRef(null);

    const [isShowResultModal, setIsShowResultModal] = useState(false)
    const [isStreaming, setIsStreaming] = useState(false);

    const [permission, requestPermission] = useCameraPermissions()

    const captureFrame = useCallback(async () => {
        console.log("CAPTURE" + cameraRef.current + "-" + isStreaming)
        try {
            const options = {
                quality: 0.3,
                base64: true,
                width: 320,
                height: 240
            };

            const data = await cameraRef.current.takePictureAsync(options);

            if (socketRef.current) {
                console.log(data.base64)
                // socketRef.current.emit('/ws/video', {
                //     frame: data.base64,
                //     timestamp: Date.now(),
                //     width: options.width,
                //     height: options.height
                // });
                socketRef.current.send({bytes:data.base64})
            }
        } catch (error) {
            console.log('Ошибка захвата кадра:', error);
        }
    }, [socketRef])

    const launchStream = useCallback(() => {
        setIsStreaming(true);
        streamIntervalRef.current = setInterval(captureFrame, 200); // 5 FPS
    }, [captureFrame])

    const stopStream = () => {
        if (streamIntervalRef.current) {
            clearInterval(streamIntervalRef.current);
            streamIntervalRef.current = null;
        }
        setIsStreaming(false);
    }

    useEffect(() => {
        console.log("USE_EFFECT")
        socketRef.current = new WebSocket("ws://localhost:8000/api/ws/video") //io("ws://localhost:8000/ws/video")
        return () => {
            if (socketRef.current) {
                //socketRef.current.disconnect();
                socketRef.current.close()
            }
            if (streamIntervalRef.current) {
                clearInterval(streamIntervalRef.current);
            }
            stopStream()
        };
    }, []);


    if (!permission) { return <View /> }

    if (!permission.granted) {
        return (
            <View style={styles.container} width='100%' height='100%'>
                <Center p='$10'>
                    <Card>
                        <VStack p='$5'>
                            <Text mb='$10' size='2xl' style={styles.message}>Необходимо разрешить доступ к камере</Text>
                            <Button onPress={requestPermission} title="grant permission">
                                <ButtonText>Разрешить</ButtonText>
                            </Button>
                        </VStack>
                    </Card>
                </Center>
            </View>
        );
    }

    return (
        <>
            <HStack style={styles.container}>
                <VStack style={styles.container_buttons} p='$1'>
                    <Heading size='lg' m='$5'>Набор №12312312312</Heading>
                    <Card>
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

                            <Button mb='$3' onPress={setIsShowResultModal.bind(null, true)}>
                                <ButtonText>Зафиксировать</ButtonText>
                            </Button>
                            <Button variant='outline'>
                                <ButtonText>Загрузить фото</ButtonText>
                            </Button>
                            <Button variant='outline'>
                                <ButtonText>Загрузить архив</ButtonText>
                            </Button>
                        </VStack>
                    </Card>
                </VStack>
                <VStack style={styles.container_camera} p='$10'>
                    <CameraView
                        ref={cameraRef}
                        style={styles.camera}
                        onCameraReady={() => {
                            console.log("READY")
                            launchStream()
                        }}
                    />
                </VStack>
            </HStack>
            <ResultModal
                isOpen={isShowResultModal}
                isSuccessScan={false}
                onClose={setIsShowResultModal.bind(null, false)}
                onContinueClick={setIsShowResultModal.bind(null, false)}
            />
        </>
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
        flex: 70,
        'clip-path': 'inset(0% 0% 0% 0% round 20px)',
        backgroundColor: 'grey',
    }
})