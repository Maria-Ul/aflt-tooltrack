import { StyleSheet } from 'react-native'
import React, { useEffect, useState } from 'react'
import {
    AddIcon, Button, Text, ButtonText, Card,
    Center, Divider, FlatList, Heading, HStack,
    Icon, Input, InputField, InputIcon, InputSlot,
    ScrollView, SearchIcon, TrashIcon, VStack,
    ChevronsUpDownIcon,
    ChevronDownIcon,
    AccordionHeader,
    AccordionTrigger,
    AccordionIcon,
    AccordionTitleText,
    AccordionContent,
    Accordion,
    AccordionItem,
    AccordionContentText,
    ChevronUpIcon,
    ChevronLeftIcon
} from '@gluestack-ui/themed'
import ToolTypeNameInputModal from './ToolTypeNameInputModal'
import { createToolTypeRequest } from '../../../../api/new/tool_types/create_tool_type'
import { getToolTypeTree } from '../../../../api/new/tool_types/get_tool_type_tree'
import { deleteToolTypeRequest } from '../../../../api/new/tool_types/delete_tool_type'
import { CrossIcon, Folder, FolderOpen, FolderPlus, PlusIcon, Wrench, X } from 'lucide-react-native'

const ToolTypeCreateScreen = ({ navigation }) => {
    var [cvClassesList, setCvClassesList] = useState([
        "PASSATIGI",
        "OTKRYVASHKA_OIL_CAN",
        "BOKOREZY",
        "SHARNITSA",
        "KOLOVOROT",
        "RAZVODNOY_KEY",
        "PASSATIGI_CONTROVOCHNY",
        "KEY_ROZGKOVY_NAKIDNOY_3_4",
        "OTVERTKA_PLUS",
        "OTVERTKA_MINUS",
        "OTVERTKA_OFFSET_CROSS"])
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
    const onDeleteToolTypeClick = (toolTypeId) => {
        deleteToolTypeRequest(
            {
                toolTypeId: toolTypeId,
                onSuccess: () => { loadToolTypeTree() }
            }
        )
    }

    const onSaveClick = (typeName) => {
        createToolTypeRequest({
            name: typeName,
            category_id: isRootCategoryAdd ? null : selectedItem.id,
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
        <ScrollView w="100%" h="100%">
            <Center p="$10">
                <Card w="100%" h="100%">
                    <HStack justifyContent='space-between'>
                        <HStack alignItems='center'>
                            <Button onPress={onBackPressed} mr="$5">
                                <Icon as={ChevronLeftIcon} color="white" />
                            </Button>
                            <Heading>Добавление типа инструмента</Heading>
                        </HStack>
                        <HStack alignItems='center'>
                            <Input variant='rounded' mr="$5" w="300px">
                                <InputSlot p="$3">
                                    <InputIcon as={SearchIcon} />
                                </InputSlot>
                                <InputField
                                    w="500px"
                                    value={searchQuery}
                                    onChangeText={setSearchQuery}
                                    placeholder='Поиск по типам и категориям' />
                            </Input>
                            <Button onPress={onAddRootCategoryClick}>
                                <Icon as={FolderPlus} color="white" />
                            </Button>
                        </HStack>
                    </HStack>
                    <Divider mt="$5" mb="$5" />
                    {searchResult != null && searchResult.length > 0 ?
                        <FlatList
                            mb="$5"
                            data={searchResult}
                            renderItem={
                                ({ item, index, separators }) => {
                                    console.log(item)
                                    return item.is_item ?
                                        <ToolTypeCreateItem
                                            data={item}
                                            onDeleteItem={onDeleteToolTypeClick}
                                        /> :
                                        <ToolTypeCreateCategoryItem
                                            data={item}
                                            onAddSubCategory={onAddCategoryClick}
                                            onAddSubItem={onAddToolTypeClick}
                                            onDeleteItem={onDeleteToolTypeClick}
                                        />
                                }
                            }
                            keyExtractor={item => item.id}
                        />
                        : <Text>Категории инструментов не найдены</Text>
                    }
                </Card>
            </Center>
            <ToolTypeNameInputModal
                classesList={cvClassesList}
                isOpen={isOpenNameInputModal}
                isCategory={isCategoryModal}
                onClose={onCloseModal}
                onContinueClick={onSaveClick}
            />
        </ScrollView>
    )
}

const ToolTypeCreateItem = ({ data, onDeleteItem }) => {
    return (
        <VStack px="$5">
            <HStack justifyContent='space-between' alignItems='center'>
                <HStack py="$5">
                    <Icon as={Wrench} mr="$3" />
                    <Text>{data.name}</Text>
                </HStack>
                <Button action="negative" onPress={onDeleteItem.bind(null, data.id)}>
                    <Icon as={X} color="white" />
                </Button>
            </HStack>
            <Divider />
        </VStack>
    )
}

const ToolTypeCreateCategoryItem = ({
    data,
    onDeleteItem,
    onAddSubItem,
    onAddSubCategory,
}) => {
    useEffect(() => {
        console.log("TYPE_TREE", data.id)
    }, [])

    return (
        <Accordion bgColor="red">
            <AccordionItem value={`item${data.id}`}>
                <AccordionHeader>
                    <AccordionTrigger>
                        {({ isExpanded }) => {
                            return (
                                <>
                                    {isExpanded ? (
                                        <AccordionIcon as={FolderOpen} mr='$3' />
                                    ) : (
                                        <AccordionIcon as={Folder} mr='$3' />
                                    )}
                                    <AccordionTitleText>
                                        {data.name}
                                    </AccordionTitleText>
                                    {isExpanded ?
                                        <HStack space='md'>
                                            <Button onPress={onAddSubItem.bind(null, data)}>
                                                <Icon as={PlusIcon} color="white" />
                                            </Button>
                                            <Button
                                                action='positive'
                                                onPress={onAddSubCategory.bind(null, data)}
                                            >
                                                <Icon as={FolderPlus} color="white" />
                                            </Button>
                                            <Button
                                                action='negative'
                                                onPress={onDeleteItem.bind(null, data.id)}
                                            >
                                                <Icon as={X} color="white" />
                                            </Button>
                                        </HStack> : <></>
                                    }

                                </>
                            );
                        }}
                    </AccordionTrigger>
                </AccordionHeader>
                <AccordionContent p="0" pl="$4">
                    {data.children != null && data.children.length > 0 ?
                        <FlatList
                            mb='$5'
                            data={data.children}
                            renderItem={
                                ({ item, index, separators }) => {
                                    return item.is_item ?
                                        <ToolTypeCreateItem
                                            data={item}
                                            onDeleteItem={onDeleteItem}
                                        /> :
                                        <ToolTypeCreateCategoryItem data={item}
                                            onAddSubItem={onAddSubItem}
                                            onAddSubCategory={onAddSubCategory}
                                            onDeleteItem={onDeleteItem}
                                        />
                                }
                            }
                            keyExtractor={item => item.id}
                        /> : <Text p="$5">В данной категории ничего не найдено</Text>
                    }
                    <AccordionContentText></AccordionContentText>
                </AccordionContent>
            </AccordionItem>
        </Accordion >

        // <VStack my="$2" space='$3'>
        //     <HStack justifyContent='space-between'>
        //         <Heading>{data.name}</Heading>
        //         <HStack>
        //             <Button action='positive' onPress={onAddSubCategory.bind(null, data)}>
        //                 <Icon as={AddIcon} color="white" />
        //             </Button>
        //             <Button action='negative' onPress={onDeleteItem.bind(null, data.id)}>
        //                 <Icon as={TrashIcon} color="white" />
        //             </Button>
        //         </HStack>
        //     </HStack>
        //     <Divider />
        //     <HStack>
        //         <HStack width='2px' bgColor='black' mr="$5" />
        //         <FlatList
        //             data={data.children}
        //             renderItem={
        //                 ({ item, index, separators }) => {
        //                     return item.is_item ?
        //                         <ToolTypeCreateItem
        //                             data={item}
        //                             onDeleteItem={onDeleteItem}
        //                         /> :
        //                         <ToolTypeCreateCategoryItem data={item}
        //                             onAddSubItem={onAddSubItem}
        //                             onAddSubCategory={onAddSubCategory}
        //                             onDeleteItem={onDeleteItem}
        //                         />
        //                 }
        //             }
        //             keyExtractor={item => item.id}
        //         />
        //     </HStack>

        //     <Button onPress={onAddSubItem.bind(null, data.id)}>
        //         <ButtonText>
        //             Добавить тип инстурмента в категорию
        //         </ButtonText>
        //     </Button>
        // </VStack>
    )
}

export default ToolTypeCreateScreen

const styles = StyleSheet.create({})
