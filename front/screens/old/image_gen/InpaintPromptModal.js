import React, { useEffect } from "react";
import {
    Box, Button, ButtonIcon, ButtonText, Card, Center, CheckCircleIcon, ChevronDownIcon, CloseCircleIcon, CloseIcon, DownloadIcon,
    HStack, Heading, Icon, Image, Modal, ModalBackdrop, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ScrollView, Select, SelectBackdrop, SelectContent, SelectDragIndicator, SelectDragIndicatorWrapper, SelectIcon, SelectInput, SelectItem, SelectPortal, SelectTrigger, Text, Textarea, TextareaInput, TrashIcon, VStack
} from "@gluestack-ui/themed"
import { useRef, useState } from "react";

export const InpaintPromtModal = ({
    isOpen,
    onClose,
    onPositivePromptChanged,
    onNegativePromptChanged,
    onGenerateInpaintClick,
}) => {
    const ref = useRef(null)

    const [positivePrompt, setPositivePrompt] = useState('')
    const [negativePrompt, setNegativePrompt] = useState('')
    useEffect(() => {
        onPositivePromptChanged(positivePrompt)
    }, [positivePrompt])
    useEffect(() => {
        onNegativePromptChanged(negativePrompt)
    }, [negativePrompt])

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
                        <Heading size="lg">Редактирование выбранной области</Heading>
                    </VStack>
                    <ModalCloseButton>
                        <Icon as={CloseIcon} />
                    </ModalCloseButton>
                </ModalHeader>
                <ModalBody>
                    <VStack space="md" m="0$">
                        <Textarea m="0$" w="100%">
                            <TextareaInput value={positivePrompt} onChangeText={setPositivePrompt} placeholder="Промт" />
                        </Textarea>
                        <Textarea m="0$" w="100%">
                            <TextareaInput value={negativePrompt} onChangeText={setNegativePrompt} placeholder="Негативный промт" />
                        </Textarea>
                    </VStack>
                </ModalBody>
                <ModalFooter>
                    <HStack>
                        <Button
                            isDisabled={positivePrompt == ""}
                            onPress={onGenerateInpaintClick.bind(null, positivePrompt, negativePrompt)}
                        >
                            <ButtonText>Сгенерировать</ButtonText>
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