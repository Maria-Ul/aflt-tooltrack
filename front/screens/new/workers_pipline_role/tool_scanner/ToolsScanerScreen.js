import { Button, ButtonText, Card, Center, Heading, HStack, Icon, Text, View, VStack } from '@gluestack-ui/themed'
import { CameraView, useCameraPermissions } from 'expo-camera'
import { getDocumentAsync } from 'expo-document-picker'
import { TriangleAlertIcon } from 'lucide-react-native'
import { useCallback, useEffect, useRef, useState } from 'react'
import { StyleSheet } from 'react-native'
import Svg, { Polyline } from 'react-native-svg'
import { getToolkitWithTools } from '../../../../api/new/tool_sets/get_tool_set_with_tools'
import ResultModal from './ResultModal'
import ToolItem from './ToolItem'

// использовать Grid
const ToolsScanerScreen = ({ route, navigation }) => {
    const { requestWithRelations } = route.params
    const [toolkitWithRelations, setToolkitWithRelations] = useState(null)

    useEffect(() => {
        console.log("TOOLS_SCANNER", requestWithRelations)
        if (requestWithRelations != null) {
            getToolkitWithTools({
                id: requestWithRelations.tool_set.id,
                onSuccess: (data) => {
                    setToolkitWithRelations(data)
                }
            })
        }
    }, [requestWithRelations])

    const cameraRef = useRef(null)
    const socketRef = useRef(null)
    const streamIntervalRef = useRef(null);

    const [isShowResultModal, setIsShowResultModal] = useState(false)
    const [isStreaming, setIsStreaming] = useState(false);

    const [width, setWidth] = useState(0)
    const [height, setHeight] = useState(0)

    const [isShowMessAlert, setIsShowMessAlert] = useState(false)

    const [boxes, setBoxes] = useState([])

    const [paths, setPaths] = useState([])

    useEffect(() => {
        setPaths(boxes.map(
            p => `${p.x1 * width},${p.y1 * height} ${p.x2 * width},${p.y2 * height} ${p.x3 * width},${p.y3 * height} ${p.x4 * width},${p.y4 * height} ${p.x1 * width},${p.y1 * height} ${p.x2 * width},${p.y2 * height}`))
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
        streamIntervalRef.current = setInterval(captureFrame, 1000); // 5 FPS
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
    //             {
    //     "classes": [
    //         "KEY_ROZGKOVY_NAKIDNOY_3_4"
    //     ],
    //     "fps": 1.46137537072815,
    //     "frame_number": 55,
    //     "masks": [],
    //     "obb_rows": [
    //         [
    //             1,
    //             192,
    //             385,
    //             384,
    //             342,
    //             397,
    //             400,
    //             205,
    //             443
    //         ]
    //     ],
    //     "probs": [
    //         0.537562251091003
    //     ],
    //     "timestamp": 1759332023.89741,
    //     "type": "frame_received"
    // }
    const onDetectionEvent = (event) => {
        const nBoxes = event.obb_rows
        const classes = event.classes
        const probs = event.probs
        console.log(event)
        if (nBoxes != null) {
            //console.log(nBoxes)
            var oBoxes = []
            nBoxes.forEach((b, index, a) => {
                const classNum = nBoxes[index][0]
                oBoxes.push({
                    x1: 1-nBoxes[index][1],
                    y1: nBoxes[index][2],
                    x2: 1-nBoxes[index][3],
                    y2: nBoxes[index][4],
                    x3: 1-nBoxes[index][5],
                    y3: nBoxes[index][6],
                    x4: 1-nBoxes[index][7],
                    y4: nBoxes[index][8],
                }
                )
            })
            console.log(oBoxes)
            setBoxes(oBoxes)
        }
    }

    useEffect(() => {
        console.log("USE_EFFECT")
        socketRef.current = new WebSocket("ws://localhost:8000/api/ws/video") //io("ws://localhost:8000/ws/video")
        socketRef.current.onmessage = (event) => {
            onDetectionEvent(JSON.parse(event.data))
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
                        }} viewBox={`0 0 ${width} ${height}`}
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