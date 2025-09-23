import React, { useEffect } from "react";
import {
    Box, Button, ButtonIcon, ButtonText, Card, Center, CheckCircleIcon, ChevronDownIcon, CloseCircleIcon, CloseIcon, DownloadIcon,
    HStack, Heading, Image,  Icon, Modal, ModalBackdrop, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ScrollView, Select, SelectBackdrop, SelectContent, SelectDragIndicator, SelectDragIndicatorWrapper, SelectIcon, SelectInput, SelectItem, SelectPortal, SelectTrigger, Text, Textarea, TextareaInput, TrashIcon, VStack
} from "@gluestack-ui/themed"
import { ActivityIndicator, Pressable, StyleSheet, TouchableOpacity, View } from "react-native"
import { EXTRA_COLOR } from "../../ColorConst";
import { useRef, useState } from "react";
import { TASK_TYPE_BANNER, TASK_TYPE_INPAINT, generateRequest } from "../../api/generate";
import { InpaintModal } from "./InpaintModal";
import { InpaintPromtModal } from "./InpaintPromptModal";
import { BannerModal } from "./BannerModal";
import { getImageRequest } from "../../api/getImage";
import { BACKEND_URL } from "../../api/baseApi";
import { deleteImageRequest } from "../../api/deleteImage";

export const STATUS_CREATED = "created"
export const STATUS_DONE = "done"
// source={{uri:`data:image/webp;base64,${image}`}}
const ImageResponseItem = ({
    status,
    imageId,
    //generationDate, 
    //bannerType, 
    productType,
    originalPromt,
    imageName,
    imageWidth,
    imageHeight,
    onRefersh
    //onAddToBannerClick,
}) => {
    const [showInpaintModal, setShowInpaintModal] = useState(false)
    const [showInpaintPromtModal, setShowInpaintPromtModal] = useState(false)
    const [inpaintPositivePromt, setInpaintPositivePromt] = useState("")
    const [inpaintNegativePromt, setInpaintNegativePromt] = useState("")

    const [showBannerModal, setShowBannerModal] = useState(false)
    const [bannerType, setBannerType] = useState("")
    const [contentPosition, setContentPosition] = useState("")
    const [bannerColor, setBannerColor] = useState("")

    const closeInpaintModal = () => { setShowInpaintModal(false) }
    const closeInpaintPromptModal = () => { setShowInpaintPromtModal(false) }
    const closeBannerModal = () => { setShowBannerModal(false) }

    const imageDisplayName = `${imageId}_${productType}_${imageWidth}x${imageHeight}`
    // Любой URI к placeholder изображению
    const [imageData, setImageData] = useState("https://analytics-space.ru/static-backend/images/img-placeholder.png")

    const [inpaintPath, setInpaintPath] = useState("")

    const onAddToBannerClick = () => {
        generateRequest(
            {
                taskType: TASK_TYPE_BANNER,
                taskData: {
                    image_id: imageId,
                    type: bannerType,
                    position: contentPosition,
                    color: bannerColor,
                }
            }
        )

        setShowBannerModal(false)
        setShowInpaintModal(false)
        setShowInpaintPromtModal(false)
        onRefersh()
    }

    const onGenerateInapintClick = () => {
        generateRequest(
            {
                taskType: TASK_TYPE_INPAINT,
                taskData: {
                    image_id: imageId,
                    mask: inpaintPath,
                    positive_prompt: inpaintPositivePromt,
                    negative_prompt: inpaintNegativePromt,
                }
            }
        )

        setShowBannerModal(false)
        setShowInpaintModal(false)
        setShowInpaintPromtModal(false)
        onRefersh()
    }

    const onDeleteItemClick = () => {
        deleteImageRequest(
            {
                imageId: imageId,
                onSuccess: () => {
                    onRefersh()
                }
            }
        )
    }

    const onLoadImageClick = () => {

    }
    return (
        <View>
            <HStack>
                <Box w="30%"></Box>
                <Card
                    //style={styles.generatedItem}
                    w="70%"
                    mb="$4"
                    P="$5"
                    variant="elevated"
                >
                    {
                        status == STATUS_DONE ? <VStack space="lg">
                            <Center>
                                <TouchableOpacity onPress={setShowInpaintModal.bind(null, true)}>
                                    <Image
                                        style={styles.generatedImage}
                                        backgroundColor={EXTRA_COLOR}
                                        source={{ uri: `http://109.248.37.46:4000/image/${imageName}` }}
                                    />
                                </TouchableOpacity>
                            </Center>
                            <Heading>{imageDisplayName}</Heading>
                            <Text>{originalPromt}</Text>
                            <HStack space="md">
                                {/* <Button onPress={onLoadImageClick}>
                                    <ButtonIcon as={DownloadIcon} />
                                </Button> */}
                                <Button onPress={onDeleteItemClick} variant="outline">
                                    <ButtonIcon as={TrashIcon} />
                                </Button>
                                {/* <Button variant="outline">
                             <ButtonIcon as={CheckCircleIcon} />
                         </Button> */}
                            </HStack>
                        </VStack> :
                            <HStack space="md">
                                <ActivityIndicator/>
                                <Text>Задача создана...</Text>
                                <Button onPress={onDeleteItemClick} variant="outline">
                                    <ButtonIcon as={TrashIcon} />
                                </Button>
                            </HStack>
                    }
                </Card>
            </HStack>
            <InpaintModal
                isOpen={showInpaintModal}
                imageData={imageData}
                imageWidth={imageWidth}
                imageHeight={imageHeight}
                onClose={closeInpaintModal}
                imageName={imageName}
                originalPromt={originalPromt}
                onAddToBannerClick={setShowBannerModal.bind(null, true)}
                onEditAreaClcik={setShowInpaintPromtModal.bind(null, true)}
                onPathChanged={(path) => { setInpaintPath(path) }}
            />
            <InpaintPromtModal
                isOpen={showInpaintPromtModal}
                onClose={closeInpaintPromptModal}
                onPositivePromptChanged={(prompt) => { setInpaintPositivePromt(prompt) }}
                onNegativePromptChanged={(prompt) => { setInpaintNegativePromt(prompt) }}
                onGenerateInpaintClick={onGenerateInapintClick}
            />
            <BannerModal
                isOpen={showBannerModal}
                onClose={closeBannerModal}
                onBannerTypeChanged={(type) => { setBannerType(type) }}
                onBannerColorChanged={(color) => { setBannerColor(color) }}
                onContentPositionChanged={(position) => { setContentPosition(position) }}
                onAddToBannerClick={onAddToBannerClick}
            />
        </View>
    )
}

export default ImageResponseItem;

const styles = StyleSheet.create({
    generatedImage: {
        resizeMode: "contain",
        minHeight: "30em",
        minWidth: "30em",
        maxWidth: "35em",
        maxHeight: "35em",
    },
    imagePreview: {
        height: "80vh",
        width: "80vh",
        left: 0,
        right: 0
    },
    generatedItem: {
        height: "40em",
        width: "40em",
    }
})

