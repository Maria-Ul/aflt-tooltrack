import { StyleSheet } from 'react-native'
import React, { useCallback, useEffect, useMemo, useState } from 'react'
import { Accordion, AccordionContent, AccordionContentText, AccordionHeader, AccordionIcon, AccordionItem, AccordionTitleText, AccordionTrigger, AddIcon, Button, ButtonText, Card, Center, ChevronLeftIcon, Divider, FlatList, Heading, HStack, Icon, Input, InputField, ScrollView, VStack } from '@gluestack-ui/themed'
import { Text } from '@gluestack-ui/themed'
import { getToolTypeTree } from '../../../../api/new/tool_types/get_tool_type_tree'
import { Folder, FolderOpen, MinusIcon, Wrench } from 'lucide-react-native'

const ToolkitTypeCreateScreen = ({ navigation }) => {
  var [toolkitTypeName, setToolkitTypeName] = useState("")
  var [toolkitTypeDescription, setToolkitTypeDescription] = useState("")
  var [toolTypeTree, setToolTypeTree] = useState([])
  var [addedItemsIds, setAddedItemsIds] = useState([])

  const loadToolTypeTree = () => {
    getToolTypeTree({
      onSuccess: (data) => {
        setToolTypeTree(data)
      }
    })
  }

  useEffect(() => {
    loadToolTypeTree()
  }, [])

  const onAddToolkitType = () => {

  }

  const onAddTool = (toolTypeId) => {
    var n = addedItemsIds.concat([toolTypeId])
    console.log("TOOL_TYPE_ID" + toolTypeId + ":" + n)
    setAddedItemsIds(n)
  }

  const onRemoveTool = (toolTypeId) => {
    var i = addedItemsIds.indexOf(toolTypeId)
    if (i > -1) {
      addedItemsIds.splice(i, 1)
    }
    setAddedItemsIds(addedItemsIds.concat([]))
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
              <Heading>Создание типа набора инструментов</Heading>
            </HStack>
            <Divider />
            <HStack>
              <VStack w="50%" justifyContent='space-between' p="$5">
                <VStack space="md">
                  <Input>
                    <InputField value={toolkitTypeName}
                      onChangeText={setToolkitTypeName}
                      placeholder="Введите наименование типа набора" />
                  </Input>
                  <Input>
                    <InputField
                      value={toolkitTypeDescription}
                      onChangeText={setToolkitTypeDescription}
                      placeholder="Введите описание (необязательно)" />
                  </Input>
                </VStack>
                <Button action='positive' onPress={onAddToolkitType}>
                  <ButtonText>Добавить тип набора</ButtonText>
                </Button>
              </VStack>
              <Divider orientation='vertical' />
              <VStack w="50%">
                <Text p="$3" size='lg' bold={true}>Выберите состав набора</Text>
                <Divider />
                <ToolsPicker
                  toolTypesTree={toolTypeTree}
                  addedToolsIds={addedItemsIds}
                  onAddTool={onAddTool}
                  onRemoveTool={onRemoveTool}
                />
              </VStack>
            </HStack>
          </VStack>
        </Card>
      </Center>
    </ScrollView>
  )
}

const ToolsPicker = ({
  toolTypesTree,
  addedToolsIds,
  onAddTool,
  onRemoveTool,
}) => {
  return (
    <>
      {toolTypesTree != null && toolTypesTree.length > 0 ?
        <FlatList
          mb="$5"
          data={toolTypesTree}
          renderItem={({ item, index, separators }) => {
            return item.is_item ?
              <ToolTypePickerItem
                data={item}
                toolsCount={toolsCount}
                onAddTool={onAddTool}
                onRemoveTool={onRemoveTool}
              /> :
              <ToolTypePickerCategoryItem
                data={item}
                addedToolsIds={addedToolsIds}
                onAddTool={onAddTool}
                onRemoveTool={onRemoveTool}
              />
          }}
          keyExtractor={item => item.id}
        />
        : <Text>Категории инструментов не найдены</Text>
      }
    </>
  )
}

const ToolTypePickerItem = ({
  data,
  addedToolsIds,
  onAddTool,
  onRemoveTool
}) => {
  var toolsCount = (addedToolsIds || []).filter(t => t == data.id).length
  return (
    <VStack px="$5">
      <HStack justifyContent='space-between' alignItems='center'>
        <HStack py="$5">
          <Icon as={Wrench} mr="$3" />
          <Text>{data.name}</Text>
        </HStack>
        <HStack>
          <Button action='positive' onPress={onAddTool.bind(null, data.id)}>
            <Icon as={AddIcon} color="white" />
          </Button>
          {toolsCount == 0 ?
            <></>
            :
            <HStack space='$3'>
              <Text>{toolsCount}</Text>
              <Button action='negative' onPress={onRemoveTool.bind(null, data.id)}>
                <Icon as={MinusIcon} color="white" />
              </Button>
            </HStack>
          }
        </HStack>
      </HStack>
      <Divider />
    </VStack>

  )
}

const ToolTypePickerCategoryItem = ({
  data,
  addedToolsIds,
  onAddTool,
  onRemoveTool,
}) => {
  ///var renderer = useCallback(, [addedToolsIds, onAddTool, onRemoveTool])

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
              renderItem={({ item, index, separators }) => {
                return item.is_item ?
                  <ToolTypePickerItem
                    data={item}
                    addedToolsIds={addedToolsIds}
                    onAddTool={onAddTool}
                    onRemoveTool={onRemoveTool}
                  /> :
                  <ToolTypePickerCategoryItem
                    data={item}
                    addedToolsIds={addedToolsIds}
                    onAddTool={onAddTool}
                    onRemoveTool={onRemoveTool}
                  />
              }}
              keyExtractor={item => item.id}
            /> : <Text p="$5">В данной категории ничего не найдено</Text>
          }
          <AccordionContentText></AccordionContentText>
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  )
}

export default ToolkitTypeCreateScreen

const styles = StyleSheet.create({})