import React, { useEffect } from "react";
import {
    Box, Button, ButtonIcon, ButtonText, Card, Center, CheckCircleIcon, ChevronDownIcon, CloseCircleIcon, CloseIcon, DownloadIcon,
    HStack, Heading, Icon, Image, Modal, ModalBackdrop, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ScrollView, Select, SelectBackdrop, SelectContent, SelectDragIndicator, SelectDragIndicatorWrapper, SelectIcon, SelectInput, SelectItem, SelectPortal, SelectTrigger, Text, Textarea, TextareaInput, TrashIcon, VStack
} from "@gluestack-ui/themed"
import { Pressable, StyleSheet, TouchableOpacity, View } from "react-native"
import { useRef, useState } from "react";
import FullWidthImage from "react-native-fullwidth-image";
import { Polyline, Svg } from "react-native-svg";
import { BACKEND_URL } from "../../api/baseApi";

export const InpaintModal = ({
    isOpen,
    imageData,
    imageWidth,
    imageHeight,
    onClose,
    imageName,
    originalPromt,
    onAddToBannerClick,
    onEditAreaClcik,
    onPathChanged,
}) => {
    const ref = useRef(null)

    const [points, setPoints] = useState([])
    const [path, setPath] = useState("");
    useEffect(() => {
        setPath(points.map(p => `${p.x},${p.y}`).join(' '))
        onPathChanged(path)
        console.log(path)
    }, [points])
    const handlePressEvent = (event) => {
        console.log(event)
        setPoints([
            ...points, { x: event.nativeEvent.offsetX, y: event.nativeEvent.offsetY }
        ])
        console.log(points)
    }
    const clearPoints = () => {
        setPoints([])
    }

    const drawPoints = (pointsArg) => {
        console.log("test")
        return pointsArg.map(point => {
            return (
                <TouchableOpacity key={point.x + point.y} style={{
                    padding: 10,
                    top: point.y - 15,
                    left: point.x - 15,
                    position: "absolute",
                    elevation: 10,
                    width: 30,
                    height: 30
                }}>
                    <View
                        style={{
                            borderWidth: 5,
                            borderColor: "red",
                            width: 10,//Math.abs(boxSize.width),
                            height: 10,//Math.abs(boxSize.height),
                        }}
                    ></View>
                </TouchableOpacity>
            );
        })
    }
    return (
        <Modal
            isOpen={isOpen}
            onClose={onClose}
            finalFocusRef={ref}
            size="full"
            p="$20"
        >
            <ModalBackdrop />
            <ModalContent m="$20">
                <ModalHeader>
                    <VStack>
                        <Heading size="lg">{imageName}</Heading>
                        <Text>{originalPromt}</Text>
                        <Text>{`Выбрано точек: ${points.length}`}</Text>
                    </VStack>
                    <ModalCloseButton>
                        <Icon as={CloseIcon} />
                    </ModalCloseButton>
                </ModalHeader>
                <ModalBody>
                    <Center w="100%" h="100%">
                        <ScrollView>
                            <Box>
                                <Pressable onPress={(event) => handlePressEvent(event)}>
                                    <FullWidthImage
                                        width={imageWidth}
                                        height={imageHeight}
                                        source={{ uri: `http://109.248.37.46:4000/image/${imageName}` }}
                                    />
                                    <Svg style={{
                                        elevation: 10,
                                        position: "absolute",
                                        top: 0,
                                        left: 0,
                                        height: imageHeight,
                                        width: imageWidth,
                                        //backgroundColor: "red"
                                    }} viewBox={`0 0 ${imageWidth} ${imageHeight}`}>
                                        <Polyline
                                            points={path}
                                            fill="#ff23234f"
                                            stroke={"red"}
                                            strokeWidth="5"
                                        />
                                    </Svg>
                                    {drawPoints(points)}
                                </Pressable>
                            </Box>
                        </ScrollView>
                    </Center>
                </ModalBody>
                <ModalFooter>
                    <HStack space="md">
                        <Button onPress={onEditAreaClcik} isDisabled={!(points.length > 2)}>
                            <ButtonText>Изменить выделенную область</ButtonText>
                        </Button>
                        <Button action="negative" isDisabled={!(points.length > 0)}>
                            <ButtonText onPress={clearPoints}>Убрать выделение</ButtonText>
                        </Button>
                        <Button onPress={onAddToBannerClick}>
                            <ButtonText>Добавить на баннер</ButtonText>
                        </Button>
                        <Button variant="outline" onPress={onClose}>
                            <ButtonText>Закрыть</ButtonText>
                        </Button>
                    </HStack>
                </ModalFooter>
            </ModalContent>
        </Modal>
    )
}