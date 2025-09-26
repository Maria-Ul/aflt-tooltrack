import { Button, ButtonText, Center, CloseIcon, Heading, HStack, Icon, Input, InputField, Modal, ModalBackdrop, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, VStack } from "@gluestack-ui/themed"
import { useRef, useState } from "react"
import React from 'react'

const ToolTypeNameInputModal = ({
    isOpen,
    isCategory,
    onClose,
    onContinueClick,
}) => {
    const [nameInput, setNameInput] = useState("")

    const ref = useRef(null)

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
                        <Heading size="lg">{
                            isCategory ? "Введите наименование группы/подгруппы" :
                                "Введите наименование инструмента"
                        }</Heading>
                    </VStack>
                    <ModalCloseButton>
                        <Icon as={CloseIcon} />
                    </ModalCloseButton>
                </ModalHeader>
                <ModalBody>
                    <VStack space="md">
                        <Center>
                            <Input>
                                <InputField value={nameInput} onChangeText={setNameInput} />
                            </Input>
                        </Center>
                    </VStack>
                </ModalBody>
                <ModalFooter>
                    <HStack>
                        <Button
                            onPress={onContinueClick.bind(null, nameInput)}
                            mr='$5'
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

export default ToolTypeNameInputModal