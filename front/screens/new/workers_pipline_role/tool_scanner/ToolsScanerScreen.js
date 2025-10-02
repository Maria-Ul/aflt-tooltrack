import { Text, Box, Button, ButtonText, Card, Center, CheckIcon, Divider, Heading, HStack, Icon, ScrollView, View, VStack } from '@gluestack-ui/themed'
import { CameraView, useCameraPermissions } from 'expo-camera'
import { getDocumentAsync } from 'expo-document-picker'
import { TriangleAlertIcon } from 'lucide-react-native'
import { useCallback, useEffect, useRef, useState } from 'react'
import { Alert, StyleSheet } from 'react-native'
import Svg, { Polyline } from 'react-native-svg'
import { getToolkitWithTools } from '../../../../api/new/tool_sets/get_tool_set_with_tools'
import ResultModal from './ResultModal'
import ToolItem from './ToolItem'
import { BACKEND_URL, WEB_SOCKET_URL } from '../../../../api/baseApi'
import { sendImageToPredictRequest } from '../../../../api/new/send_image/send_image_to_predict'
import { sendZipToPredictRequest } from '../../../../api/new/send_image/send_zip_to_predict'
import { BOKOREZY_CLASS } from '../../warehouse_employee_role/tool_type/ToolTypeCreateScreen'
import { CONFIDENCE_THRESHOLD } from '../../../../App'
import { completeServiceRequest } from '../../../../api/new/service_request/complete_service_request'
import { EMPLOYEE_NUMBER_ROUTE } from '../../Screens'
import { markIncidentRequest } from '../../../../api/new/service_request/mark_incident_request'
import alert from '../../../../components/SimpleAlert'

// const classesRusNames = new Map(Object.entries(
//     {
//         BOKOREZY: "Бокорезы",
//         PASSATIGI: "Пассатижи",
//         SHARNITSA: "Шэрница",
//         KOLOVOROT: "Коловорот",
//         RAZVODNOY_KEY: "Разводной ключ",
//         PASSATIGI_CONTROVOCHNY: "Пассатижи центровочные",
//         KEY_ROZGKOVY_NAKIDNOY_3_4: "Ключ рожковый/накидной 3/4",
//         OTVERTKA_PLUS: "Отвертка +",
//         OTVERTKA_MINUS: "Отвертка -",
//         OTVERTKA_OFFSET_CROSS: "Отвертка на смещенный крест",
//         OTKRYVASHKA_OIL_CAN: "Открывашка для банок с маслом",
//     }
// ))

const colorsArr = [
    "#594f32",
    "#a677af",
    "#555787",
    "#383d0c",
    "#898979",
    "#563d96",
    "#84013e",
    "#576655",
    "#713bd6",
    "#3f8c2c",
    "#15261c",
    "#999ed8",
    "#83c9ef",
    "#0b0219",
    "#181919",
]

const classColorsMap = new Map(Object.entries(
    {
        BOKOREZY: colorsArr[0],
        PASSATIGI: colorsArr[0],
        SHARNITSA: colorsArr[0],
        KOLOVOROT: colorsArr[0],
        RAZVODNOY_KEY: colorsArr[0],
        PASSATIGI_CONTROVOCHNY: colorsArr[0],
        KEY_ROZGKOVY_NAKIDNOY_3_4: colorsArr[0],
        OTVERTKA_PLUS: colorsArr[0],
        OTVERTKA_MINUS: colorsArr[0],
        OTVERTKA_OFFSET_CROSS: colorsArr[0],
        OTKRYVASHKA_OIL_CAN: colorsArr[0],
    }
))

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
    const [isShowSuccessAlert, setIsShowSuccessModal] = useState(false)

    const [boxes, setBoxes] = useState([])
    const [paths, setPaths] = useState([])
    const [classes, setClasses] = useState([])
    const [probs, setProbs] = useState([])

    useEffect(() => {
        setPaths(boxes.map(
            p => `${p.x1 * width},${p.y1 * height} ${p.x2 * width},${p.y2 * height} ${p.x3 * width},${p.y3 * height} ${p.x4 * width},${p.y4 * height} ${p.x1 * width},${p.y1 * height} ${p.x2 * width},${p.y2 * height}`))
    }, [boxes, width, height])

    const [permission, requestPermission] = useCameraPermissions()
    //Alert.alert("Нет доступа к камере")
    // useEffect(() => {
    //     if (!permission) {

    //     } else if (permission != null && !permission.granted) {
    //         //Alert.alert("Нет доступа к камере")
    //         //requestPermission()
    //     }
    // }, [permission])

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
        streamIntervalRef.current = setInterval(captureFrame, 2000);
    }, [captureFrame])

    const stopStream = () => {
        if (streamIntervalRef.current) {
            clearInterval(streamIntervalRef.current);
            streamIntervalRef.current = null;
        }
        setIsStreaming(false);
    }

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
        setIsShowMessAlert(event.overlap_flag)
        console.log(event)
        if (nBoxes != null) {
            //console.log(nBoxes)
            setIsShowSuccessModal(probs.length == classColorsMap.length &&
                probs.every(p => p > CONFIDENCE_THRESHOLD))
            var oBoxes = []
            nBoxes.forEach((b, index, a) => {
                const classNum = nBoxes[index][0]
                oBoxes.push({
                    x1: 1 - nBoxes[index][1],
                    y1: nBoxes[index][2],
                    x2: 1 - nBoxes[index][3],
                    y2: nBoxes[index][4],
                    x3: 1 - nBoxes[index][5],
                    y3: nBoxes[index][6],
                    x4: 1 - nBoxes[index][7],
                    y4: nBoxes[index][8],
                }
                )
            })
            console.log(oBoxes)
            setBoxes(oBoxes)
            setClasses(classes)
            setProbs(probs)
        }
    }

    const onModalFinishClick = useCallback((comment) => {
        if (isShowSuccessAlert) {
            completeServiceRequest({
                request_id: requestWithRelations.id,
                onSuccess: () => {
                    navigation.navigate(EMPLOYEE_NUMBER_ROUTE)
                }
            })
        } else {
            markIncidentRequest({
                request_id: requestWithRelations.id,
                comment: comment,
                onSuccess: () => {
                    navigation.navigate(EMPLOYEE_NUMBER_ROUTE)
                    alert("Внимание!", "Инцидент передан в работу службе контроля качества")
                },
                onError: () => {
                    console.log("ERROR")
                    
                    alert("Внимание!", "В системе нет специалистов контроля качества для" + 
                        "назначения инцидентов или инцидент для данной заявки уже создан")
                }
            })
        }
    }, [isShowSuccessAlert, requestWithRelations])

    useEffect(() => {
        console.log("USE_EFFECT")
        socketRef.current = new WebSocket(WEB_SOCKET_URL + "/api/ws/video") //io("ws://localhost:8000/ws/video")
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


    // if (!permission) {
    //     console.log("Не удалось получить доступ к камере")
    //     //return <View /> 
    // }

    // if (!permission.granted) {
    //     console.log("Не удалось получить доступ к камере!")
    //     // return (
    //     //     <View style={styles.container} width='100%' height='100%'>
    //     //         <Center p='$10'>
    //     //             <Card>
    //     //                 <VStack p='$5'>
    //     //                     <Text mb='$10' size='2xl' style={styles.message}>Необходимо разрешить доступ к камере</Text>
    //     //                     <Button onPress={requestPermission} title="grant permission">
    //     //                         <ButtonText>Разрешить</ButtonText>
    //     //                     </Button>
    //     //                 </VStack>
    //     //             </Card>
    //     //         </Center>
    //     //     </View>
    //     // );
    // }

    return (
        <ScrollView horizontal={true} flex={1}>
            <HStack flex={1}>
                <Box flex={30} position='relative' width="25%" bg="$backgroundLight0" padding="$2">
                    <Heading size='lg' mb="$3">{`Набор ${toolkitWithRelations != null ? toolkitWithRelations.batch_number : "-"}`}</Heading>
                    <VStack space='md'>
                        <Button mb='$3' onPress={setIsShowResultModal.bind(null, true)}>
                            <ButtonText>Сдать</ButtonText>
                        </Button>
                        <Divider />
                        <Text>Для тестирования:</Text>
                        <Button variant='outline' onPress={onUploadPhotoClick}>
                            <ButtonText>Загрузить фото</ButtonText>
                        </Button>
                        <Button variant='outline' onPress={onUploadZipClick}>
                            <ButtonText>Загрузить архив</ButtonText>
                        </Button>
                    </VStack>
                    <ScrollView flex={1}>
                        <VStack space='$5'>
                            <Text size='lg' mb='$5'>Инструменты в наборе:</Text>
                            {
                                toolkitWithRelations != null ?
                                    toolkitWithRelations.tool_set_type.tool_types.map((toolType) => {
                                        const classIndex = classes.indexOf(toolType.tool_class)
                                        const toolProb = probs[classIndex]
                                        const classColor = classColorsMap.get(toolType.tool_class)
                                        //console.log("CLASS_COLOR", classColor)
                                        return (<ToolItem
                                            color={classColor}
                                            name={toolType.name}
                                            probability={toolProb}
                                            threshold={CONFIDENCE_THRESHOLD}
                                        />)
                                    })
                                    : <>Загрузка данных о наборе</>
                            }
                        </VStack>
                    </ScrollView>
                </Box>

                <Box flex={70} position='relative'>
                    <View p='$3'
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
                            {permission == null || !permission.granted ?
                                <Text style={{
                                    position: 'absolute',
                                    top: '40px',
                                    left: '40px',
                                }} size='lg' bold={true}>Видео с веб-камеры недоступно</Text> : <></>}

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
                                {paths.map((p, index) => {
                                    return (
                                        <>
                                            <Polyline
                                                fill="transparent"
                                                points={p}
                                                stroke={colorsArr[index]}
                                                strokeWidth="2px"
                                            />
                                        </>
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
                            {isShowSuccessAlert ? <SuccessAlert
                                style={{
                                    position: 'absolute',
                                    top: 0,
                                    right: 0,
                                }}
                            /> : <></>}
                        </View>
                    </View>
                </Box>
            </HStack >
            <ResultModal
                isOpen={isShowResultModal}
                isSuccessScan={isShowSuccessAlert}
                onClose={setIsShowResultModal.bind(null, false)}
                onContinueClick={onModalFinishClick}
            />
        </ScrollView >
        // <ScrollView>
        //     <HStack style={styles.container}>
        //         <VStack style={styles.container_buttons} p='$1'>
        //             <Heading size='lg' m='$5'>{`Набор ${toolkitWithRelations != null ? toolkitWithRelations.batch_number : "-"}`}</Heading>
        //             <Card>
        //                 <VStack p='$5' mb='$9' space='$5'>
        //                     <Text size='lg' mb='$5'>Инструменты в наборе:</Text>
        //                     {
        //                         toolkitWithRelations != null ?
        //                             toolkitWithRelations.tool_set_type.tool_types.map((toolType) => {
        //                                 const classIndex = classes.indexOf(toolType.tool_class)
        //                                 const toolProb = probs[classIndex]
        //                                 const classColor = classColorsMap.get(toolType.tool_class)
        //                                 //console.log("CLASS_COLOR", classColor)
        //                                 return (<ToolItem
        //                                     color={classColor}
        //                                     name={toolType.name}
        //                                     probability={toolProb}
        //                                     threshold={CONFIDENCE_THRESHOLD}
        //                                 />)
        //                             })
        //                             : <>Загрузка данных о наборе</>
        //                     }
        //                     <VStack space='md'>
        //                         <Button mb='$3' onPress={setIsShowResultModal.bind(null, true)}>
        //                             <ButtonText>Сдать</ButtonText>
        //                         </Button>
        //                         <Divider />
        //                         <Text>Для тестирования:</Text>
        //                         <Button variant='outline' onPress={onUploadPhotoClick}>
        //                             <ButtonText>Загрузить фото</ButtonText>
        //                         </Button>
        //                         <Button variant='outline' onPress={onUploadZipClick}>
        //                             <ButtonText>Загрузить архив</ButtonText>
        //                         </Button>
        //                     </VStack>

        //                 </VStack>
        //             </Card>
        //         </VStack>
        //         <VStack>
        //             <View p='$10'
        //                 style={styles.container_camera}>
        //                 <View onLayout={(event) => {
        //                     const { x, y, width, height } = event.nativeEvent.layout
        //                     setHeight(height)
        //                     setWidth(width)
        //                     console.log("SIZE:" + x + " " + y + " " + width + " " + height)
        //                 }} style={styles.container_camera} >
        //                     <CameraView
        //                         mode='video'
        //                         ratio='4:3'
        //                         videoQuality='4:3'
        //                         ref={cameraRef}
        //                         style={styles.camera}
        //                         onCameraReady={() => {
        //                             console.log("READY")
        //                             console.log(paths[0])
        //                             launchStream()
        //                         }}
        //                     />
        //                     <Text style={{
        //                         position: 'absolute',
        //                         top: 0,
        //                         left: 0,
        //                         zIndex: 0,
        //                     }} size='lg' bold={true}>Видео с веб-камеры</Text>
        //                     <Svg style={{
        //                         elevation: 10,
        //                         position: "absolute",
        //                         zIndex: 1,
        //                         //top: '$10',
        //                         //left: '$10',
        //                         //backgroundColor: "red"
        //                     }} viewBox={`0 0 ${width} ${height}`}
        //                         height={`${height}px`}
        //                         width={`${width}px`}
        //                     >
        //                         {paths.map((p, index) => {
        //                             return (
        //                                 <>
        //                                     <Polyline
        //                                         fill="transparent"
        //                                         points={p}
        //                                         stroke={colorsArr[index]}
        //                                         strokeWidth="2px"
        //                                     />
        //                                 </>
        //                             )
        //                         })}
        //                     </Svg>
        //                     {isShowMessAlert ? <MessAlert
        //                         style={{
        //                             position: 'absolute',
        //                             top: 0,
        //                             right: 0,
        //                         }}
        //                     /> : <></>}
        //                     {isShowSuccessAlert ? <SuccessAlert
        //                         style={{
        //                             position: 'absolute',
        //                             top: 0,
        //                             right: 0,
        //                         }}
        //                     /> : <></>}
        //                 </View>
        //             </View>
        //         </VStack>
        //     </HStack >
        //     <ResultModal
        //         isOpen={isShowResultModal}
        //         isSuccessScan={false}
        //         onClose={setIsShowResultModal.bind(null, false)}
        //         onContinueClick={setIsShowResultModal.bind(null, false)}
        //     />
        // </ScrollView>
    )
}

const MessAlert = ({ style }) => {
    return (
        <HStack style={style} p="$3" space='md' bgColor='#f79494ff'
            borderWidth="2px" borderColor='#ff0000ff' alignItems='center'>
            <Icon as={TriangleAlertIcon} size='xl' />
            <Text size="lg" bold="true">{`Кажется, инструменты перекрывают друга друга.\n
            Попробуйте разложить их более равномерно`}</Text>
        </HStack>
    )
}

const SuccessAlert = ({ style }) => {
    return (
        <HStack style={style} p="$3" space='md' bgColor='#94f794ff'
            borderWidth="2px" borderColor='#2fff00ff' alignItems='center'>
            <Icon as={CheckIcon} size='xl' />
            <Text size="lg" bold="true">{`Все инструменты из набора распознаны\nМожно завершить приемка`}</Text>
        </HStack>
    )
}

export default ToolsScanerScreen

const styles = StyleSheet.create({
    container: {
        flex: 100,
    },
    container_buttons: {
        flex: 20,
    },
    container_camera: {
        flex: 70,
        width: "1200px",
        height: "900px",
        aspectRatio: '4:3',

    },
    camera: {
        //width: "640px",
        //height: "480px",
        width: "1200px",
        height: "900px",
        flex: 1,
        aspectRatio: '4:3',
        borderWidth: "2px",
        borderColor: "grey",
        backgroundColor: 'tranparent',
        'clip-path': 'inset(0% 0% 0% 0% round 20px)',
    }
})