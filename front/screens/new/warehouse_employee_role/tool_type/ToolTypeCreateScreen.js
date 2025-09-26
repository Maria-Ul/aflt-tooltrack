import { StyleSheet, Text, View } from 'react-native'
import React, { useEffect, useState } from 'react'
import { AddIcon, Button, ButtonText, Card, Center, Divider, FlatList, Heading, HStack, Icon, Input, InputField, InputIcon, InputSlot, ScrollView, SearchIcon, TrashIcon, VStack } from '@gluestack-ui/themed'
import ToolTypeNameInputModal from './ToolTypeNameInputModal'
import { createToolTypeRequest } from '../../../../api/new/tool_types/create_tool_type'
import { getToolTypeTree } from '../../../../api/new/tool_types/get_tool_type_tree'

const ToolTypeCreateScreen = ({ navigation }) => {
    var [toolTypeTree, setToolTypeTree] = useState(null)
    var [searchResult, setSearchResult] = useState(null)
    var [searchQuery, setSearchQuery] = useState("")
    var [isOpenNameInputModal, setIsOpenNameInputModal] = useState(false)
    var [isCategoryModal, setIsCategoryModal] = useState(true)
    var [isRootCategoryAdd, setIsRootCategoryAdd] = useState(true)
    var [selectedItem, setSelectedItem] = useState(null)

    const loadToolTypeTree = () => {
        getToolTypeTree({
            onSuccess: (data) => {
                setToolTypeTree(data)
            }
        })
    }

    const onCloseModal = () => {
        setIsOpenNameInputModal(false)
    }

    const onAddRootCategoryClick = () => {
        setIsCategoryModal(true)
        setIsOpenNameInputModal(true)
        setIsRootCategoryAdd(true)
    }
    const onAddCategoryClick = (parentCategoryData) => {
        setIsCategoryModal(true)
        setIsOpenNameInputModal(true)
        setIsRootCategoryAdd(false)
        setSelectedItem(parentCategoryData)
    }
    const onAddToolTypeClick = (parentCategoryData) => {
        setIsCategoryModal(false)
        setIsOpenNameInputModal(true)
        setIsRootCategoryAdd(false)
        setSelectedItem(parentCategoryData)
    }
    const onDeleteCategoryClick = ({ categoryId }) => {

    }
    const onDeleteToolTypeClick = ({ toolTypeId }) => {

    }

    const onSaveClick = (typeName) => {
        createToolTypeRequest({
            name: typeName,
            category_id: isRootCategoryAdd ? null : selectedItem.categor_id,
            is_item: !isCategoryModal,
            onSuccess: () => {
                onCloseModal()
                loadToolTypeTree()
            }
        })
    }

    const onBackPressed = () => {
        navigation.goBack()
    }


    useEffect(() => {
        loadToolTypeTree()
    }, [])

    useEffect(() => {
        console.log(toolTypeTree)
        setSearchResult(toolTypeTree)
    }, [toolTypeTree, searchQuery])

    return (
        <>
            <Center p="$10">
                <Card w="100%" h="100%">
                    <ScrollView h="100%">
                        <HStack justifyContent='space-between'>
                            <Heading>Добавление типа инструмента</Heading>
                            <HStack>
                                <Input variant='rounded' mr="$5">
                                    <InputSlot p="$3">
                                        <InputIcon as={SearchIcon} />
                                    </InputSlot>
                                    <InputField value={searchQuery} onChangeText={setSearchQuery} placeholder='Поиск по типам и категориям' />
                                </Input>
                            </HStack>
                        </HStack>
                        <Divider mt="$5" mb="$5" />
                        <FlatList
                            data={searchResult}
                            renderItem={
                                ({ item, index, separators }) => {
                                    console.log(item)
                                    return item.is_item ?
                                        <ToolTypeCreateItem data={item} /> :
                                        <ToolTypeCreateCategoryItem
                                            data={item}
                                            onAddSubCategory={onAddCategoryClick.bind(null, item)}
                                            onAddSubItem={onAddToolTypeClick.bind(null, item)}
                                            onDeleteCategory={onDeleteCategoryClick.bind(null, item.id)}
                                            onDeleteItem={onDeleteToolTypeClick.bind(null, item.id)}
                                        />
                                }
                            }
                            keyExtractor={item => item.id}
                        />
                    </ScrollView>
                    <Button onPress={onAddRootCategoryClick}>
                        <ButtonText>Добавить корневую категорию</ButtonText>
                    </Button>
                    <Button onPress={onBackPressed} variant='outline'>
                        <ButtonText>Назад</ButtonText>
                    </Button>
                </Card>
            </Center>
            <ToolTypeNameInputModal
                isOpen={isOpenNameInputModal}
                isCategory={isCategoryModal}
                onClose={onCloseModal}
                onContinueClick={onSaveClick}
            />
        </>
    )
}

const ToolTypeCreateItem = ({ data, onDeleteItem }) => {
    return (
        <HStack>
            <Text>{data.name}</Text>
            <Button>
                <Icon as={TrashIcon} onPress={onDeleteItem} />
            </Button>
        </HStack>
    )
}

const ToolTypeCreateCategoryItem = ({
    data,
    onDeleteItem,
    onAddSubItem,
    onAddSubCategory,
    onDeleteCategory,
}) => {
    return (
        <VStack>
            <HStack>
                <Heading>{data.name}</Heading>
                <Button action='positive' onPress={onAddSubCategory.bind(null, data)}>
                    <Icon as={AddIcon} color="white" />
                </Button>
                <Button action='negative' onPress={onDeleteCategory}>
                    <Icon as={TrashIcon} color="white" />
                </Button>
            </HStack>
            <FlatList
                data={data.children}
                renderItem={
                    ({ item, index, separators }) => {
                        return item.is_item ?
                            <ToolTypeCreateItem data={item} onDeleteItem={onDeleteItem.bind(null, item.id)} /> :
                            <ToolTypeCreateCategoryItem data={item}
                                onAddSubItem={onAddSubItem.bind(null, item)}
                                onAddSubCategory={onAddSubCategory.bind(null, item)}
                                onDeleteCategory={onDeleteCategory.bind(null, item.id)}
                                onDeleteItem={onDeleteItem.bind(null, item.id)}
                            />
                    }
                }
                keyExtractor={item => item.id}
            />
            <Button onPress={onAddSubItem.bind(null, data.id)}>
                <ButtonText>
                    Добавить тип инстурмента в категорию
                </ButtonText>
            </Button>
        </VStack>
    )
}

export default ToolTypeCreateScreen

const styles = StyleSheet.create({})