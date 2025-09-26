import { StyleSheet } from 'react-native'
import React, { useEffect, useState } from 'react'
import { TOOL_TYPE_CREATE_ROUTE } from '../../Screens'
import { AddIcon, Box, Button, Card, Center, Divider, FlatList, Heading, HStack, Icon, Input, InputField, InputIcon, InputSlot, ScrollView, SearchIcon, VStack } from '@gluestack-ui/themed'
import { getToolTypeTree } from '../../../../api/new/tool_types/get_tool_type_tree'

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
    <Center p="$10">
      <Card w="100%" h="100%">
        <ScrollView h="100%">
          <HStack justifyContent='space-between'>
            <Heading>Список типов инструментов</Heading>
            <HStack>
              <Input variant='rounded' mr="$5">
                <InputSlot p="$3">
                  <InputIcon as={SearchIcon} />
                </InputSlot>
                <InputField
                  value={searchQuery}
                  onChangeText={setSearchQuery}
                  placeholder='Поиск по типам инструментов и категориям' />
              </Input>
              <Button onPress={onAddClick}>
                <Icon color="white" as={AddIcon} />
              </Button>
            </HStack>

          </HStack>
          <Divider mt="$5" mb="$5" />
          <FlatList
            data={searchResult}
            renderItem={
              ({ item, index, separators }) => {
                return item.is_item ? <ToolTypeItem data={item} /> : <ToolTypeCategoryItem data={item} />
              }
            }
            keyExtractor={item => item.id}
          />
        </ScrollView>
      </Card>
    </Center>
  )
}

const ToolTypeItem = ({ data }) => {
  return (
    <VStack>
      <Text>{data.name}</Text>
    </VStack>
  )
}

const ToolTypeCategoryItem = ({ data }) => {
  return (
    <HStack>
      <Heading>{data.name}</Heading>
      <FlatList
        data={data.children}
        renderItem={
          ({ item, index, separators }) => {
            return item.is_item ?
              <ToolTypeItem data={item} /> :
              <ToolTypeCategoryItem data={item} />
          }
        }
        keyExtractor={item => item.id}
      />
    </HStack>
  )
}

export default ToolTypeListScreen

const styles = StyleSheet.create({})