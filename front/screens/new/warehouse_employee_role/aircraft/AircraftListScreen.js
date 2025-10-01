import { FlatList, StyleSheet } from 'react-native'
import React, { useEffect, useState } from 'react'
import { ButtonText, Card, Heading, HStack, ScrollView, Text, Button, Center, Icon, AddIcon, EditIcon, VStack, Divider, Box, Input, InputField, InputSlot, InputIcon, SearchIcon } from '@gluestack-ui/themed'
import { AIRCRAFT_CREATE_ROUTE } from '../../Screens'
import { getAllAircraftsRequest } from '../../../../api/new/aircraft/get_all_aircrafts'
import { Plane } from 'lucide-react-native'

const AircraftListScreen = ({ navigation }) => {
  var [aircraftsList, setAircraftsList] = useState(null)
  var [searchResult, setSearchResult] = useState(null)
  var [searchQuery, setSearchQuery] = useState("")

  const loadAircrafts = () => {
    getAllAircraftsRequest({
      onSuccess: (data) => {
        setAircraftsList(data)
      }
    })
  }

  const onAddClick = () => {
    console.log("ON_ADD")
    navigation.navigate(AIRCRAFT_CREATE_ROUTE)
  }

  useEffect(() => {
    loadAircrafts()
  }, [])

  useEffect(() => {
    if (aircraftsList != null) {
      //console.log(aircraftsList)
      const filtered = aircraftsList.filter( item => 
        item.tail_number.includes(searchQuery)
      )
      //console.log(filtered)
      setSearchResult(filtered)
    }
  }, [aircraftsList, searchQuery])

  return (
    <Center p="$10">
      <Card w="100%" h="100%">
        <ScrollView h="100%">
          <HStack justifyContent='space-between'>
            <Heading>Список воздушного транспорта</Heading>
            <HStack>
              <Input variant='rounded' mr="$5">
                <InputSlot p="$3">
                  <InputIcon as={SearchIcon} />
                </InputSlot>
                <InputField value={searchQuery} onChangeText={setSearchQuery} placeholder='Найти борт' />
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
                return <AircraftListItem
                  data={item}
                />
              }
            }
            keyExtractor={item => item.id}
          />
        </ScrollView>
      </Card>
    </Center>
  )
}

const AircraftListItem = ({ data, onCreateRequest, onEdit }) => {
  return (
    <HStack justifyContent='space-between' alignItems='center' mb="$5">
      <HStack>
        <Box h="$20" w="$5" bgColor="blue" />
        <VStack pl="$5">
          <Icon as={Plane}/>
          <Text bold={true} size='lg' >{data.tail_number}</Text>
          <Text size='md'>{data.model}</Text>
        </VStack>
      </HStack>


      <HStack space="md">
        {/* <Button onPress={onCreateRequest}>
          <ButtonText>Создать заявку на обслуживание</ButtonText>
        </Button>
        <Button color='orange' variant='outline' onPress={onEdit}>
          <Icon as={EditIcon} />
        </Button> */}
      </HStack>
    </HStack>
  )
}

export default AircraftListScreen

const styles = StyleSheet.create({})