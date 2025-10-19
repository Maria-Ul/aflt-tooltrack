import { Text, Box, Button, ButtonText, Card, Center, CheckIcon, Divider, Heading, HStack, Icon, ScrollView, View, VStack, } from '@gluestack-ui/themed'
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
import { Col, Grid, Row } from 'react-native-easy-grid'
import { loginRequest } from '../../../../api/new/login'
import { createServiceRequest } from '../../../../api/new/service_request/create_service_request'
import { getRequestWithRelations } from '../../../../api/new/service_request/get_request_with_relations'
import CameraPreview from './CameraPreview'
import AuthStagePreview from './AuthStagePreview'
import AuthStageMenu from './AuthStageMenu'
import { REQUEST_CREATED, REQUEST_IN_PROGRESS } from '../../warehouse_employee_role/maintainance_request/RequestsListScreen'
import ScanningResultMenu from './ScanningResultMenu'
import { getAllServiceRequests } from '../../../../api/new/service_request/get_all_service_requests'

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

const FAST_FLOW_ENGINEER_TAB_NUMBER = "333333"
const FAST_FLOW_WORKER_ID = 3

const FastToolsScanerScreen = ({ route, navigation }) => {
    const [isAuthStage, setIsAuthStage] = useState(true)
    const [isAuthTimerActive, setTimerActive] = useState(false);

    const startTimer = () => {
        setTimerActive(true);
        setTimeout(() => {
            setIsAuthStage(prevFlag => !prevFlag);
            setTimerActive(false);
        }, 3000);
    };

    useEffect(() => {
        startTimer()
    }, [])

    const [requestWithRelations, setRequestWithRelation] = useState(null)
    const [toolkitWithRelations, setToolkitWithRelations] = useState(null)
    const [isIssuingTools, setIsIssuingTools] = useState(null)
    useEffect(() => {
        if (!isAuthStage) {
            loginRequest({
                username: "222222",
                password: "12345678",
                onSuccess: () => {
                    // Получаем все заявки для текущего тестового пользователя
                    getAllServiceRequests({
                        workerId: FAST_FLOW_WORKER_ID,
                        onSuccess: (serviceRequestsList) => {
                            console.log("GET_ALL_REQUESTS", serviceRequestsList)
                            // Если есть заявки в процессе, запускаем приемку
                            var requestInProgress = serviceRequestsList.find(r => r.status == REQUEST_IN_PROGRESS)
                            if (requestInProgress != null) {
                                getRequestWithRelations({
                                    request_id: requestInProgress.id,
                                    onSuccess: (requestWR) => {
                                        setIsIssuingTools(false)
                                        setRequestWithRelation(requestWR)
                                    }
                                })
                            } else {
                                // Иначе, если есть открытые заявки, запускаем выдачу
                                var createdRequest = serviceRequestsList.find(r => r.status == REQUEST_CREATED)

                                if (createdRequest != null) {
                                    getRequestWithRelations({
                                        request_id: createdRequest.id,
                                        onSuccess: (requestWR) => {
                                            setIsIssuingTools(true)
                                            setRequestWithRelation(requestWR)
                                        }
                                    })
                                } else {
                                    // Если и открытой заявки не нашлось, создаем заявку
                                    createServiceRequest({
                                        aircraft_id: 1,
                                        warehouse_employee_id: 1,
                                        aviation_engineer_id: 2,
                                        tool_set_id: 2,
                                        status: REQUEST_CREATED,
                                        description: `заявка от ${Date.now()}`,
                                        onSuccess: (requestData) => {
                                            getRequestWithRelations({
                                                request_id: requestData.id,
                                                onSuccess: (requestWR) => {
                                                    setIsIssuingTools(true)
                                                    setRequestWithRelation(requestWR)
                                                }
                                            })
                                        },
                                    })
                                }
                            }
                        }, onError: () => { }
                    },)
                },
            })
        }
    }, [isAuthStage])




    // const loadRequestByWorkerId = (workerId) => {
    //     console.log("load")

    // }

    // useEffect(() => {
    //     loginRequest({
    //         username: "333333",
    //         password: "12345678",
    //         onSuccess: () => {
    //             getRequestWithRelations
    //             createServiceRequest({
    //                 aircraft_id: 1,
    //                 warehouse_employee_id: 1,
    //                 aviation_engineer_id: 3,
    //                 tool_set_id: 2,
    //                 status: "",
    //                 description: `заявка от ${Date.now()}`,
    //                 onSuccess: () => { },
    //             })
    //         },
    //     })
    // })

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


    const socketRef = useRef(null)


    const [isShowResultModal, setIsShowResultModal] = useState(false)

    const [isShowMessAlert, setIsShowMessAlert] = useState(false)
    const [isShowSuccessAlert, setIsShowSuccessModal] = useState(false)


    const [boxes, setBoxes] = useState([])
    const [classes, setClasses] = useState([])
    const [probs, setProbs] = useState([])



    const onDetectionEvent = useCallback((event) => {
        const eventData = JSON.parse(event.data)
        const nBoxes = eventData.obb_rows
        const classes = eventData.classes
        const probs = eventData.probs
        setIsShowMessAlert(eventData.overlap_flag)
        console.log(eventData)
        if (nBoxes != null) {
            console.log("SUCCESS", toolkitWithRelations != null)
            //console.log(nBoxes)
            if (toolkitWithRelations != null) {
                const success = probs.length == toolkitWithRelations.tool_set_type.tool_types.length &&
                    probs.every(p => p > CONFIDENCE_THRESHOLD)
                console.log("SUCCESS", success)
                setIsShowSuccessModal(success)
            }
            var oBoxes = []
            nBoxes.forEach((b, index, a) => {
                const classNum = b[0]
                oBoxes.push({
                    x1: 1 - b[1],
                    y1: b[2],
                    x2: 1 - b[3],
                    y2: b[4],
                    x3: 1 - b[5],
                    y3: b[6],
                    x4: 1 - b[7],
                    y4: b[8],
                }
                )
            })
            console.log(oBoxes)
            setBoxes(oBoxes)
            setClasses(classes)
            setProbs(probs)
        }
    }, [toolkitWithRelations])

    const onModalFinishClick = useCallback((comment) => {
        if (isShowSuccessAlert) {
            setSendFrames(false)
            completeServiceRequest({
                request_id: requestWithRelations.id,
                onSuccess: () => {
                    navigation.navigate(EMPLOYEE_NUMBER_ROUTE)
                    alert("Заявка переведена в статус ЗАВЕРШЕНА")
                }
            })
        } else {
            markIncidentRequest({
                request_id: requestWithRelations.id,
                comment: comment,
                onSuccess: () => {

                },
                onError: () => {

                }
            })
        }
    }, [isShowSuccessAlert, requestWithRelations])

    // useEffect(() => {
    //     socketRef.current.onmessage = onDetectionEvent
    // }, [toolkitWithRelations])

    return (
        <Grid>
            <Row>
                <Col size={33} style={{ padding: "15px" }}>
                    {isAuthStage ? <AuthStageMenu navigation={navigation} /> : <ScanningResultMenu
                        toolkitWithRelations={toolkitWithRelations}
                        classes={classes}
                        probs={probs}
                        onFinishButtonPressed={() => { }}
                    />}
                </Col>
                <Col size={68} style={{ padding: "15px" }}>
                    {isAuthStage ? <AuthStagePreview /> :
                        <CameraPreview
                            isShowMessAlert={isShowMessAlert}
                            isShowSuccessAlert={isShowSuccessAlert}
                            socketRef={socketRef}
                            boxes={boxes}
                        />
                    }
                </Col>
            </Row>
        </Grid>
    )
}

export default FastToolsScanerScreen

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
})