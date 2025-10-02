import { StyleSheet } from 'react-native'
import React, { useEffect, useState } from 'react'
import { AddIcon, Card, Center, Divider, FlatList, Heading, HStack, ScrollView, SearchIcon, Text, TrashIcon, VStack } from '@gluestack-ui/themed'
import { Input } from '@gluestack-ui/themed'
import { InputSlot } from '@gluestack-ui/themed'
import { InputIcon } from '@gluestack-ui/themed'
import { InputField } from '@gluestack-ui/themed'
import { Button } from '@gluestack-ui/themed'
import { Icon } from '@gluestack-ui/themed'
import { TOOLKIT_CREATE_ROUTE, TOOLKIT_TYPE_CREATE_ROUTE } from '../../Screens'
import { getAllToolkitTypes } from '../../../../api/new/tool_set_types/get_all_tool_set_types'
import { deleteToolkitTypeRequest } from '../../../../api/new/tool_set_types/delete_tool_set_type'
import { TouchableOpacity } from 'react-native'
import { getAllToolkits } from '../../../../api/new/tool_sets/get_all_tool_sets'
import { deleteToolkitRequest } from '../../../../api/new/tool_sets/delete_tool_set'
import { ToolCase } from 'lucide-react-native'

const ToolkitListScreen = ({ navigation }) => {
  var [toolkitList, setToolkits] = useState(null)
  var [searchResult, setSearchResult] = useState(null)
  var [searchQuery, setSearchQuery] = useState("")

  const loadToolkits = () => {
    getAllToolkits({
      onSuccess: (data) => {
        setToolkits(data)
      }
    })
  }

  navigation.addListener('focus', () => {
      loadToolkits()
  });

  const onAddClick = () => {
    navigation.navigate(TOOLKIT_CREATE_ROUTE, { toolkit: null })
  }

  const onDeleteToolkit = (id) => {
    deleteToolkitRequest(
      {
        toolkitId: id,
        onSuccess: () => { loadToolkits() },
      }
    )
  }

  const onPressToolkit = (data) => {
    // navigation.navigate(
    //   TOOLKIT_TYPE_CREATE_ROUTE,
    //   { toolkitType: data }
    // )
  }

  useEffect(() => {
    loadToolkits()
  }, [])

  useEffect(() => {
    if (toolkitList != null) {
      //console.log(aircraftsList)
      const filtered = toolkitList.filter(item =>
        item.batch_number.includes(searchQuery)
      )
      //console.log(filtered)
      setSearchResult(filtered)
    }
  }, [toolkitList, searchQuery])

  return (
    <ScrollView w="100%" h="100%">
      <Center p="$10">
        <Card w="100%" h="100%">
          <HStack justifyContent='space-between'>
            <Heading>Список наборов</Heading>
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
                  return <ToolkitItem
                    data={item}
                    onPress={onPressToolkit}
                    onDeleteTollkit={onDeleteToolkit}
                  />
                }
              }
              keyExtractor={item => item.id}
            />
            : <Text>Наборы не найдены</Text>
          }
        </Card>
      </Center>
    </ScrollView>
  )
}

const ToolkitItem = ({ data, onPress, onDeleteTollkit }) => {
  return (
    <TouchableOpacity onPress={onPress.bind(null, data)}>
      <VStack>
        <HStack justifyContent='space-between' my="$3">
          <HStack>
            <Icon as={ToolCase}/>
            <Text size='lg' bold={true}>{data.batch_number}</Text>
          </HStack>

          <Button onPress={onDeleteTollkit.bind(null, data.id)}>
            <Icon as={TrashIcon} color="white" />
          </Button>
        </HStack>
        <Text size="md" ml="$4" mb="$3">{data.description}</Text>
        <Divider />
      </VStack>
    </TouchableOpacity>


  )
}

export default ToolkitListScreen

const styles = StyleSheet.create({})