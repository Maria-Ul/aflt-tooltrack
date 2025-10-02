import { StyleSheet } from 'react-native'
import React, { useCallback, useRef, useState } from 'react'
import { Button, ButtonText, CloseIcon, Heading, HStack, Icon, Input, InputField, Modal, ModalBackdrop, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, Text, VStack } from '@gluestack-ui/themed'

const ResultModal = ({
    isOpen,
    isSuccessScan,
    onClose,
    onContinueClick,
}) => {
    const ref = useRef(null)
    const [comment, setComment] = useState("")

    const onCClick = useCallback(() => {
        onContinueClick(comment)
    }, [comment, onContinueClick])
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
                            isSuccessScan ? "Завершение примеки" : "Завершение приемки с инцидентом"
                        }</Heading>
                    </VStack>
                    <ModalCloseButton>
                        <Icon as={CloseIcon} />
                    </ModalCloseButton>
                </ModalHeader>
                <ModalBody>
                    <VStack space="md">
                        <Text size='md'>
                            {
                                isSuccessScan ? "Распознаны все инструменты из набора.\nЗавершить процедуру приемки?" :
                                    "Не все инструменты из набора обнаружены!\nБудет создан инцидент."
                            }
                        </Text>

                        {
                            !isSuccessScan ?
                                <Input >
                                    <InputField
                                        value={comment}
                                        onChangeText={setComment}
                                        placeholder="Введите краткое описание проблемы" />
                                </Input>
                                : <></>
                        }

                    </VStack>
                </ModalBody>
                <ModalFooter>
                    <HStack>
                        <Button
                            onPress={onCClick}
                            mr='$5'
                        >
                            <ButtonText>{
                                isSuccessScan ? "Завершить" : "Создать инцидент"
                            }</ButtonText>
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

export default ResultModal