import { Button, ButtonText, Center, ChevronDownIcon, CloseIcon, Heading, HStack, Icon, Input, InputField, Modal, ModalBackdrop, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, Select, SelectBackdrop, SelectContent, SelectDragIndicator, SelectDragIndicatorWrapper, SelectIcon, SelectInput, SelectItem, SelectPortal, SelectTrigger, VStack } from "@gluestack-ui/themed"
import { useRef, useState } from "react"
import React from 'react'

const ToolTypeNameInputModal = ({
    classesList,
    isOpen,
    isCategory,
    onClose,
    onContinueClick,
}) => {
    const [nameInput, setNameInput] = useState("")

    const selectorItems = classesList.map(c => {
        return (<SelectItem label={c} value={c} />)
    })
    console.log(selectorItems)
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
                            isCategory ? "Добавление папки" :
                                "Добавление инструмента"
                        }</Heading>
                    </VStack>
                    <ModalCloseButton>
                        <Icon as={CloseIcon} />
                    </ModalCloseButton>
                </ModalHeader>
                <ModalBody>
                    <VStack space="md">
                        <Input>
                            <InputField width="500px" value={nameInput} onChangeText={setNameInput} placeholder="Введите наименование" />
                        </Input>
                        {
                            !isCategory ? <Select>
                                <SelectTrigger size="md">
                                    <SelectInput width="500px" placeholder="Выберите распознаваемый класс инструмента" />
                                    <SelectIcon className="mr-3" as={ChevronDownIcon} />
                                </SelectTrigger>
                                <SelectPortal>
                                    <SelectBackdrop />
                                    <SelectContent>
                                        <SelectDragIndicatorWrapper>
                                            <SelectDragIndicator />
                                        </SelectDragIndicatorWrapper>
                                        {selectorItems}
                                        {/* <SelectItem label="UX Research" value="ux" />
                                        <SelectItem label="Web Development" value="web" />
                                        <SelectItem
                                            label="Cross Platform Development Process"
                                            value="Cross Platform Development Process"
                                        />
                                        <SelectItem label="UI Designing" value="ui" isDisabled={true} />
                                        <SelectItem label="Backend Development" value="backend" /> */}
                                    </SelectContent>
                                </SelectPortal>
                            </Select>
                                : <></>
                        }

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