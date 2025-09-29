import { StyleSheet } from 'react-native'
import React, { useState } from 'react'
import { AddIcon, Card, Center, Divider, FlatList, Heading, HStack, ScrollView, SearchIcon, Text } from '@gluestack-ui/themed'
import { Input } from '@gluestack-ui/themed'
import { InputSlot } from '@gluestack-ui/themed'
import { InputIcon } from '@gluestack-ui/themed'
import { InputField } from '@gluestack-ui/themed'
import { Button } from '@gluestack-ui/themed'
import { Icon } from '@gluestack-ui/themed'
import { TOOLKIT_TYPE_CREATE_ROUTE } from '../../Screens'
import { getAllToolkitTypes } from '../../../../api/new/tool_set_types/get_all_tool_set_types'

const ToolkitTypeListScreen = ({ navigation }) => {
  var [toolkitTypes, setToolkitTypes] = useState(null)
  var [searchResult, setSearchResult] = useState(null)
  var [searchQuery, setSearchQuery] = useState("")

  const loadToolkitTypes = () => {
    getAllToolkitTypes({
      onSuccess: (data) => {
        setToolkitTypes(data)
      }
    })
  }

  const onAddClick = () => {
    navigation.navigate(TOOLKIT_TYPE_CREATE_ROUTE)
  }
  return (
    <ScrollView w="100%" h="100%">
      <Center p="$10">
        <Card w="100%" h="100%">
          <HStack justifyContent='space-between'>
            <Heading>Список типов наборов</Heading>
            <HStack alignItems='center'>
              <Input variant='rounded' mr="$5" w="300px">
                <InputSlot p="$3">
                  <InputIcon as={SearchIcon} />
                </InputSlot>
                <InputField
                  w="500px"
                  value={searchQuery}
                  onChangeText={setSearchQuery}
                  placeholder='Поиск по типам наборов' />
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
                  return <ToolkitTypeItem data={item} />
                }
              }
              keyExtractor={item => item.id}
            />
            : <Text>Типы наборов не найдены</Text>
          }
        </Card>
      </Center>
    </ScrollView>
  )
}

const ToolkitTypeItem = ({ data }) => {
  <Text>{data.name}</Text>
}

export default ToolkitTypeListScreen

const styles = StyleSheet.create({})