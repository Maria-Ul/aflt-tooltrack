import { StyleSheet } from 'react-native'
import React, { useCallback, useEffect, useMemo, useState } from 'react'
import { Accordion, AccordionContent, AccordionContentText, AccordionHeader, AccordionIcon, AccordionItem, AccordionTitleText, AccordionTrigger, AddIcon, Button, ButtonText, Card, Center, ChevronLeftIcon, Divider, FlatList, Heading, HStack, Icon, Input, InputField, ScrollView, VStack } from '@gluestack-ui/themed'
import { Text } from '@gluestack-ui/themed'
import { getToolTypeTree } from '../../../../api/new/tool_types/get_tool_type_tree'
import { Folder, FolderOpen, MinusIcon, Wrench } from 'lucide-react-native'
import { createToolkitTypeRequest } from '../../../../api/new/tool_set_types/create_tool_set_type'
import { editToolkitTypeRequest } from '../../../../api/new/tool_set_types/edit_tool_set_type'
import { getToolkitTypeWithTools } from '../../../../api/new/tool_set_types/get_tool_set_with_tools'
import { createToolkitRequest } from '../../../../api/new/tool_sets/create_tool_set'
import { editToolkitRequest } from '../../../../api/new/tool_sets/edit_tool_set'
import { getAllToolkitTypes } from '../../../../api/new/tool_set_types/get_all_tool_set_types'
import ToolkitTypeSelectorModal from './ToolkitTypeSelectorModal'

const ToolkitCreateScreen = ({ route, navigation }) => {
    var [toolkitPartNumber, setToolkitPartNumber] = useState("")
    var [toolkitDescription, setToolkitDescription] = useState("")
    var [selectedToolkitType, setToolkitType] = useState(null)
    var [toolsPartNumbersMap, setToolsPartNumbersMap] = useState(new Map())

    var [toolkitTypesList, setToolkitTypesList] = useState(null)

    var [isToolkitTypeSelectorModalOpen, setIsModalOpen] = useState(false)

    const { toolkit } = route.params

    const loadToolkitTypeWithTools = (toolkitTypeId) => {
        getToolkitTypeWithTools({
            id: toolkitTypeId,
            onSuccess: (data) => {
                setToolkitType(data)
            }
        })
    }

    const loadToolkitTypesList = () => {
        getAllToolkitTypes({
            onSuccess: (data) => {
                setToolkitTypesList(data)
            }
        })
    }

    useEffect(() => {
        if (toolkit != null) {
            setToolkitPartNumber(toolkit.batch_number)
            setToolkitDescription(toolkit.description)
            setToolsPartNumbersMap(toolkit.tool_type_ids)
            loadToolkitTypeWithTools(toolkit.id)
        } else {
            loadToolkitTypesList()
        }
    }, [])

    const onAddToolkitType = () => {
        if (toolkit == null) {
            createToolkitRequest(
                {
                    toolkitTypeId: selectedToolkitType.id,
                    batchNumber: toolkitPartNumber,
                    description: toolkitDescription,
                    toolsNumbersMap: toolsPartNumbersMap,
                    onSuccess: () => {
                        navigation.goBack()
                    }
                }
            )
        } else {
            editToolkitRequest(
                {
                    id: selectedToolkitType.id,
                    batchNumber: toolkitPartNumber,
                    description: toolkitDescription,
                    onSuccess: () => {
                        navigation.goBack()
                    }
                }
            )
        }
    }

    const onSelectToolkitType = (toolkitType) => {
        getToolkitTypeWithTools({
            id: toolkitType.id,
            onSuccess: (data) => {
                setToolkitType(data)
                onCloseModal()
            }
        })
    }

    const onOpenSelector = () => {
        setIsModalOpen(true)
    }

    const onCloseModal = () => {
        setIsModalOpen(false)
    }

    const onBackPressed = () => {
        navigation.goBack()
    }
    return (
        <ScrollView>
            <Center p="$10">
                <Card w="100%" h="100%">
                    <VStack>
                        <HStack alignItems='center' mb="$3">
                            <Button onPress={onBackPressed} mr="$5">
                                <Icon as={ChevronLeftIcon} color="white" />
                            </Button>
                            <Heading>Добавление набора инструментов</Heading>
                        </HStack>
                        <Divider />
                        <HStack>
                            <VStack w="50%" justifyContent='space-between' p="$5">
                                <VStack space="md">
                                    <Input>
                                        <InputField value={toolkitPartNumber}
                                            onChangeText={setToolkitPartNumber}
                                            placeholder="Введите партийный номер набора" />
                                    </Input>
                                    <Input>
                                        <InputField
                                            value={toolkitDescription}
                                            onChangeText={setToolkitDescription}
                                            placeholder="Введите описание набора(необязательно)" />
                                    </Input>
                                    <Button onPress={onOpenSelector}>
                                        <ButtonText>Выбрать тип набора</ButtonText>
                                    </Button>
                                </VStack>
                                <Button action='positive' onPress={onAddToolkitType}>
                                    <ButtonText>{
                                        toolkit != null ? "Изменить тип набора" : "Добавить тип набора"
                                    }</ButtonText>
                                </Button>
                            </VStack>
                            <Divider orientation='vertical' />
                            <VStack w="50%">
                                <Text p="$3" size='lg' bold={true}>Cостав набора
                                    {selectedToolkitType != null ? " типа " + selectedToolkitType.name : ""}</Text>
                                <Divider />
                                {selectedToolkitType != null && selectedToolkitType.tool_types.length > 0 ?
                                    <FlatList
                                        mb="$5"
                                        data={selectedToolkitType.tool_types}
                                        renderItem={
                                            ({ item, index, separators }) => {
                                                return <ToolPartNumberInputItem
                                                    toolType={item}
                                                    partNumber={""}
                                                    onPartNumberChanged={() => { }}
                                                />
                                            }
                                        }
                                        keyExtractor={item => item.id}
                                    />
                                    : <Text>Выберите тип набора</Text>
                                }
                            </VStack>
                        </HStack>
                    </VStack>
                </Card>
                <ToolkitTypeSelectorModal
                    isOpen={isToolkitTypeSelectorModalOpen}
                    toolkitTypesList={toolkitTypesList}
                    onClose={onCloseModal}
                    onSelectToolkitType={onSelectToolkitType}
                />
            </Center>
        </ScrollView>
    )
}

const ToolPartNumberInputItem = ({ toolType, partNumber, onPartNumberChanged }) => {
    return (
        <VStack>
            <Text>{toolType.name}</Text>
            <Input>
                <InputField value={partNumber} onChangeText={onPartNumberChanged}
                    placeholder='Введите партийный номер инструмента'></InputField>
            </Input>
        </VStack>
    )
}

export default ToolkitCreateScreen

const styles = StyleSheet.create({})