import { StyleSheet } from 'react-native'
import React, { useEffect, useState } from 'react'
import { TOOL_TYPE_CREATE_ROUTE } from '../../Screens'
import { AddIcon, Box, Text, Button, Card, Center, Divider, FlatList, Heading, HStack, Icon, Input, InputField, InputIcon, InputSlot, ScrollView, SearchIcon, VStack, AccordionItem, AccordionHeader, AccordionTrigger, AccordionIcon, AccordionTitleText, AccordionContent, Accordion } from '@gluestack-ui/themed'
import { getToolTypeTree } from '../../../../api/new/tool_types/get_tool_type_tree'
import { Folder, FolderOpen, Wrench } from 'lucide-react-native'

const ToolTypeListScreen = ({ navigation }) => {
  var [toolTypeTree, setToolTypeTree] = useState(null)
  var [searchResult, setSearchResult] = useState(null)
  var [searchQuery, setSearchQuery] = useState("")

  const loadToolTypeTree = () => {
    getToolTypeTree({
      onSuccess: (data) => {
        setToolTypeTree(data)
      }
    })
  }

  const onAddClick = () => {
    console.log("ON_ADD")
    navigation.navigate(TOOL_TYPE_CREATE_ROUTE)
  }

  useEffect(() => {
    loadToolTypeTree()
  }, [])

  useEffect(() => {
    setSearchResult(toolTypeTree)
  }, [toolTypeTree, searchQuery])

  return (
    <ScrollView w="100%" h="100%">
      <Center p="$10">
        <Card w="100%" h="100%">
          <HStack justifyContent='space-between'>
            <Heading>Список типов инструментов</Heading>
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
              <Button onPress={onAddClick}>
                <Icon as={AddIcon} color="white" />
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
                    <ToolTypeItem
                      data={item}
                    /> :
                    <ToolTypeCategoryItem
                      data={item}
                    />
                }
              }
              keyExtractor={item => item.id}
            />
            : <Text>Категории инструментов не найдены</Text>
          }
        </Card>
      </Center>
    </ScrollView>
  )
}

const ToolTypeItem = ({ data }) => {
  return (
    <VStack px="$5">
      <HStack justifyContent='space-between' alignItems='center'>
        <HStack py="$5">
          <Icon as={Wrench} mr="$3" />
          <Text>{data.name}</Text>
        </HStack>
      </HStack>
      <Divider />
    </VStack>
  )
}

const ToolTypeCategoryItem = ({
  data,
}) => {
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
              renderItem={
                ({ item, index, separators }) => {
                  return item.is_item ?
                    <ToolTypeItem data={item} /> :
                    <ToolTypeCategoryItem data={item}
                    />
                }
              }
              keyExtractor={item => item.id}
            /> : <Text p="$5">В данной категории пока ничего нет</Text>
          }
        </AccordionContent>
      </AccordionItem>
    </Accordion >
  )
}

export default ToolTypeListScreen

const styles = StyleSheet.create({})