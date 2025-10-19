import { StyleSheet, View } from 'react-native'
import React, { useCallback, useEffect, useRef, useState } from 'react'
import { CameraView, useCameraPermissions } from 'expo-camera'
import Svg, { Polyline } from 'react-native-svg'
import MessAlert from './MessAlert'
import SuccessAlert from './SuccessAlert'
import { Card, Center, Text } from '@gluestack-ui/themed'
import { WEB_SOCKET_URL } from '../../../../api/baseApi'

const CameraPreview = ({
    isShowMessAlert,
    isShowSuccessAlert,
    socketRef,
    boxes,
}) => {
    const cameraRef = useRef(null)
    const [sendFrames, setSendFrames] = useState(true)
    const [permission, requestPermission] = useCameraPermissions()
    const [isStreaming, setIsStreaming] = useState(false);
    const [width, setWidth] = useState(0)
    const [height, setHeight] = useState(0)
    const [paths, setPaths] = useState([])

    const captureFrame = useCallback(async () => {
        //console.log("CAPTURE" + cameraRef.current + "-" + isStreaming)
        if (sendFrames) {
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
        }
    }, [socketRef, sendFrames])

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

    const streamIntervalRef = useRef(null);

    useEffect(() => {
        setPaths(boxes.map(
            p => `${p.x1 * width},${p.y1 * height} ${p.x2 * width},${p.y2 * height} ${p.x3 * width},${p.y3 * height} ${p.x4 * width},${p.y4 * height} ${p.x1 * width},${p.y1 * height} ${p.x2 * width},${p.y2 * height}`))
    }, [boxes, width, height])

    useEffect(() => {
        console.log("USE_EFFECT")
        socketRef.current = new WebSocket(WEB_SOCKET_URL + "/api/ws/video") //io("ws://localhost:8000/ws/video")
        return () => {
            if (socketRef.current) {
                socketRef.current.close()
            }
            if (streamIntervalRef.current) {
                clearInterval(streamIntervalRef.current);
            }
            stopStream()
        };
    }, []);


    return (
        <Card variant='elevated' height="100%" justifyContent='center' alignItems='center'
            onLayout={(event) => {
                const { x, y, width, height } = event.nativeEvent.layout
                setHeight(height)
                setWidth(width)
                console.log("SIZE:" + x + " " + y + " " + width + " " + height)
            }}>
            <Center flex={1}>
                <CameraView
                    mode='video'
                    ratio='4:3'
                    videoQuality='4:3'
                    ref={cameraRef}
                    style={
                        {
                            width: width,
                            height: height,
                            flex: 1,
                            aspectRatio: '4:3',
                            borderWidth: "2px",
                            borderColor: "grey",
                            backgroundColor: 'tranparent',
                            'clip-path': 'inset(0% 0% 0% 0% round 20px)',
                        }
                    }
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
                        right: "500px",
                    }}
                /> : <></>}
            </Center>
        </Card>

    )
}

export default CameraPreview

const styles = StyleSheet.create({
    camera: {
        width: "640px",
        height: "480px",
        flex: 1,
        //width: "100%",
        //height: "100%",
        aspectRatio: '4:3',
        borderWidth: "2px",
        borderColor: "grey",
        backgroundColor: 'tranparent',
        'clip-path': 'inset(0% 0% 0% 0% round 20px)',
    }
})