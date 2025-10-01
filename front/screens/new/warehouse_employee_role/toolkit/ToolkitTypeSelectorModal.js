import { Button, ButtonText, Center, CloseIcon, FlatList, Heading, HStack, Icon, Input, InputField, Modal, ModalBackdrop, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ScrollView, VStack } from "@gluestack-ui/themed"
import { useRef, useState } from "react"
import React from 'react'
import { ToolkitItem } from "./ToolkitListScreen"
import { ToolkitTypeItem } from "../toolkit_type/ToolkitTypeListScreen"

const ToolkitTypeSelectorModal = ({
    isOpen,
    toolkitTypesList,
    onClose,
    onSelectToolkitType,
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
                        <Heading size="lg">Выберите тип набора</Heading>
                    </VStack>
                    <ModalCloseButton>
                        <Icon as={CloseIcon} />
                    </ModalCloseButton>
                </ModalHeader>
                <ModalBody>
                    <ScrollView>
                        <VStack space="md">
                            <Center>
                                {toolkitTypesList != null && toolkitTypesList.length > 0 ?
                                    <FlatList
                                        mb="$5"
                                        data={toolkitTypesList}
                                        renderItem={
                                            ({ item, index, separators }) => {
                                                return <ToolkitTypeItem
                                                    isShowDelete={false}
                                                    data={item}
                                                    onPress={onSelectToolkitType}
                                                    onDeleteTollkitType={() => { }}
                                                />
                                            }
                                        }
                                        keyExtractor={item => item.id}
                                    />
                                    : <Text>Типы наборов не найдены</Text>
                                }
                            </Center>
                        </VStack>
                    </ScrollView>
                </ModalBody>
                <ModalFooter>
                    <HStack>
                        <Button variant="outline" onPress={onClose}>
                            <ButtonText>Закрыть</ButtonText>
                        </Button>
                    </HStack>
                </ModalFooter>
            </ModalContent>
        </Modal>
    )
}

export default ToolkitTypeSelectorModal