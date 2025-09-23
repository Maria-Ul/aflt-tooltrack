
import React, { useEffect } from "react";
import {
    Box, Button, ButtonIcon, ButtonText, Card, Center, CheckCircleIcon, ChevronDownIcon, CloseCircleIcon, CloseIcon, DownloadIcon,
    HStack, Heading, Icon, Image, Modal, ModalBackdrop, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ScrollView, Select, SelectBackdrop, SelectContent, SelectDragIndicator, SelectDragIndicatorWrapper, SelectIcon, SelectInput, SelectItem, SelectPortal, SelectTrigger, Text, Textarea, TextareaInput, TrashIcon, VStack
} from "@gluestack-ui/themed"
import { Pressable, StyleSheet, TouchableOpacity, View } from "react-native"
import { EXTRA_COLOR } from "../../ColorConst";
import { useRef, useState } from "react";
import FullWidthImage from "react-native-fullwidth-image";
import { Polyline, Svg } from "react-native-svg";
import { bannerTypes } from "../../model/banner/BannerType";
import { bannerColors } from "../../model/banner/BannerColors";
import ColorSquare from "../../components/ColorSquare";
import ColorBox from "../../components/ColorBox";

export const BannerModal = ({
    isOpen,
    onClose,
    onBannerTypeChanged,
    onBannerColorChanged,
    onContentPositionChanged,
    onAddToBannerClick,
}) => {
    const ref = useRef(null)

    const [bannerType, setBannerType] = useState("")
    const [contentPosition, setContentPosition] = useState("")
    const [backgroundColor, setBackgroundColor] = useState("")

    useEffect(() => {
        onBannerTypeChanged(bannerType)
    }, [bannerType])
    useEffect(() => {
        onBannerColorChanged(backgroundColor)
    }, [backgroundColor])
    useEffect(() => {
        onContentPositionChanged(contentPosition)
    }, [contentPosition])

    const renderBannerTypeOptions = () => {
        return bannerTypes.map(
            (type) => {
                return (
                    <SelectItem label={type.displayName} value={type.name} />
                )
            }
        )
    }
    const renderContentPositionOptions = (bannerTypeStr) => {
        if (bannerTypeStr != "") {
            selectedBannerType = bannerTypes.find((item) => item.name == bannerTypeStr)
            return selectedBannerType.availableSizes.map(
                (size) => {
                    return (
                        <SelectItem label={size.displayName} value={size.name} />
                    )
                }
            )
        }
    }
    const renderBannerColors = () => {
        return bannerColors.map(
            (color) => {
                return <TouchableOpacity onPress={setBackgroundColor.bind(null, color)}><ColorSquare colorHex={color} /></TouchableOpacity>
            }
        )
    }

    return (
        <Modal
            isOpen={isOpen}
            onClose={onClose}
            finalFocusRef={ref}
            size="lg"
            p="$20"
        >
            <ModalBackdrop />
            <ModalContent m="$20">
                <ModalHeader>
                    <VStack>
                        <Heading size="lg">Параметры баннера</Heading>
                    </VStack>
                    <ModalCloseButton>
                        <Icon as={CloseIcon} />
                    </ModalCloseButton>
                </ModalHeader>
                <ModalBody>
                    {/* <HStack space="md">
                    <Text>Добавить на баннер</Text>
                    <Switch value={isAddBanner} onValueChange={setIsAddBanner} />
                </HStack> */}
                    <VStack space="md">
                        <Text size="md">Тип баннера</Text>
                        <Select
                            selectedValue={bannerType}
                            onValueChange={setBannerType}
                        >
                            <SelectTrigger variant="outline" size="md">
                                <SelectInput placeholder="Тип форм-фактора баннера" />
                                <SelectIcon mr="$3">
                                    <Icon as={ChevronDownIcon} />
                                </SelectIcon>
                            </SelectTrigger>
                            <SelectPortal>
                                <SelectBackdrop />
                                <SelectContent>
                                    <SelectDragIndicatorWrapper>
                                        <SelectDragIndicator />
                                    </SelectDragIndicatorWrapper>
                                    {renderBannerTypeOptions()}
                                </SelectContent>
                            </SelectPortal>
                        </Select>
                        <Text size="md">Расположение изображения</Text>
                        <Select
                            selectedValue={contentPosition}
                            onValueChange={setContentPosition}
                        >
                            <SelectTrigger variant="outline" size="md">
                                <SelectInput placeholder="Расположение относительно баннера" />
                                <SelectIcon mr="$3">
                                    <Icon as={ChevronDownIcon} />
                                </SelectIcon>
                            </SelectTrigger>
                            <SelectPortal>
                                <SelectBackdrop />
                                <SelectContent>
                                    <SelectDragIndicatorWrapper>
                                        <SelectDragIndicator />
                                    </SelectDragIndicatorWrapper>
                                    {renderContentPositionOptions(bannerType)}
                                </SelectContent>
                            </SelectPortal>
                        </Select>
                        <Text size="md">Цвет баннера</Text>
                        <Center>
                            <HStack>
                                {renderBannerColors()}
                            </HStack>
                        </Center>
                        <ColorBox colorHex={backgroundColor} colorName={"Выбран цвет "} isShowText={true} />
                    </VStack>
                </ModalBody>
                <ModalFooter>
                    <HStack>
                        <Button
                            onPress={onAddToBannerClick.bind(null, bannerType, contentPosition, backgroundColor)}
                            isDisabled={!(bannerType != "" && backgroundColor != "" && contentPosition != "")}
                        >
                            <ButtonText>Добавить</ButtonText>
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