import { StyleSheet } from 'react-native'
import React, { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react'
import { CameraView, useCameraPermissions } from 'expo-camera'
import { Button, ButtonText, Center, Heading, HStack, VStack, Text, View, Card, Box, Icon } from '@gluestack-ui/themed'
import { Header } from '@rneui/themed'
import ToolItem from './ToolItem'
import WhiteCard from '../../../../components/WhiteCard'
import ResultModal from './ResultModal'
import { BACKEND_URL } from '../../../../api/baseApi'
import { io } from 'socket.io-client'
import Svg, { Polyline, Rect } from 'react-native-svg'
import { YellowBox } from 'react-native-web'
import { MessageCircleWarningIcon, TriangleAlertIcon } from 'lucide-react-native'
import { getDocumentAsync } from 'expo-document-picker'

// использовать Grid
const ToolsScanerScreen = ({ route, navigation }) => {
    const { requestId } = route.params

    const cameraRef = useRef(null)
    const socketRef = useRef(null)
    const streamIntervalRef = useRef(null);

    const [isShowResultModal, setIsShowResultModal] = useState(false)
    const [isStreaming, setIsStreaming] = useState(false);

    const [width, setWidth] = useState(0)
    const [height, setHeight] = useState(0)

    const [isShowMessAlert, setIsShowMessAlert] = useState(true)

    const [boxes, setBoxes] = useState([
        {
            x1: 0.1,
            y1: 0.1,
            x2: 0.8,
            y2: 0.2,
            x3: 0.6,
            y3: 0.5,
            x4: 0.05,
            y4: 0.7,
        },
        {
            x1: 0.05,
            y1: 0.05,
            x2: 0.75,
            y2: 0.15,
            x3: 0.55,
            y3: 0.45,
            x4: 0.00,
            y4: 0.65,
        }
    ])

    const [paths, setPaths] = useState([])

    useEffect(() => {
        setPaths(boxes.map(p => `${p.x1 * width},${p.y1 * height} ${p.x2 * width},${p.y2 * height} ${p.x3 * width},${p.y3 * height} ${p.x4 * width},${p.y4 * height} ${p.x1 * width},${p.y1 * height}`))
    }, [boxes, width, height])

    const [permission, requestPermission] = useCameraPermissions()

    const captureFrame = useCallback(async () => {
        //console.log("CAPTURE" + cameraRef.current + "-" + isStreaming)
        try {
            const options = {
                quality: 0.9,
                base64: true,
                width: 640,
                height: 480
            };

            const data = await cameraRef.current.takePictureAsync(options);

            if (socketRef.current) {
                var frameJs = `{
                    "type": "video_frame",
                    "timestamp": ${Date.now()},
                    "frame": "${data.base64}"
                }`
                //console.log(frameJs)
                socketRef.current.send(frameJs)
            }
        } catch (error) {
            console.log('Ошибка захвата кадра:', error);
        }
    }, [socketRef])

    const launchStream = useCallback(() => {
        setIsStreaming(true);
        streamIntervalRef.current = setInterval(captureFrame, 500); // 5 FPS
    }, [captureFrame])

    const stopStream = () => {
        if (streamIntervalRef.current) {
            clearInterval(streamIntervalRef.current);
            streamIntervalRef.current = null;
        }
        setIsStreaming(false);
    }

    const onUploadPhotoClick = async () => {
        var file = await getDocumentAsync({ type: ["image/jpeg", "image/png"] })
        console.log(file.assets)
    }

    const onUploadZipClick = async () => {
        var file = await getDocumentAsync({ type: 'application/zip' })
        console.log(file.assets[0])
    }

    useEffect(() => {
        console.log("USE_EFFECT")
        socketRef.current = new WebSocket("ws://localhost:8000/api/ws/video") //io("ws://localhost:8000/ws/video")
        socketRef.current.onmessage = (event) => {
            //console.log(event)
        }
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
                            <Button variant='outline' onPress={onUploadPhotoClick}>
                                <ButtonText>Загрузить фото</ButtonText>
                            </Button>
                            <Button variant='outline' onPress={onUploadZipClick}>
                                <ButtonText>Загрузить архив</ButtonText>
                            </Button>
                        </VStack>
                    </Card>
                </VStack>
                <View p='$10'
                    style={styles.container_camera}>
                    <View onLayout={(event) => {
                        const { x, y, width, height } = event.nativeEvent.layout
                        setHeight(height)
                        setWidth(width)
                        console.log("SIZE:" + x + " " + y + " " + width + " " + height)
                    }} style={styles.container_camera} >
                        <CameraView
                            mode='video'
                            ratio='4:3'
                            videoQuality='4:3'
                            ref={cameraRef}
                            style={styles.camera}
                            onCameraReady={() => {
                                console.log("READY")
                                console.log(paths[0])
                                launchStream()
                            }}
                        />
                        <Svg style={{
                            elevation: 10,
                            position: "absolute",
                            zIndex: 1,
                            //top: '$10',
                            //left: '$10',
                            //backgroundColor: "red"
                        }} //viewBox={`0 0 1000 1000`}
                            height={`${height}px`}
                            width={`${width}px`}
                        >
                            {paths.map(p => {
                                return (
                                    <Polyline
                                        points={p}
                                        fill="#ff23234f"
                                        stroke={"red"}
                                        strokeWidth="2px"
                                    />
                                )
                            })}
                        </Svg>
                        {isShowMessAlert ? <MessAlert
                            style={{
                                position: 'absolute',
                                top: 0,
                                right: 0,
                            }}
                        /> : <></>}
                    </View>
                </View>
            </HStack >
            <ResultModal
                isOpen={isShowResultModal}
                isSuccessScan={false}
                onClose={setIsShowResultModal.bind(null, false)}
                onContinueClick={setIsShowResultModal.bind(null, false)}
            />
        </>
    )
}

const MessAlert = ({ style }) => {
    return (
        <HStack style={style} p="$3" space='md' bgColor='#f79494ff' borderColor='#ff0000ff' alignItems='center'>
            <Icon as={TriangleAlertIcon} size='xl' />
            <Text size="lg" bold="true">{`Кажется, инструменты перекрывают друга друга.\nПопробуйте разложить их более равномерно`}</Text>
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
        //width: "640px",
        //height: "480px",
        'clip-path': 'inset(0% 0% 0% 0% round 20px)',
    },
    camera: {
        //width: "640px",
        //height: "480px",
        flex: 70,
        backgroundColor: 'grey',
    }
})