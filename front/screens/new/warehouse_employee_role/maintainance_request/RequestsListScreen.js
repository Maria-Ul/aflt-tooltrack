import { FlatList, StyleSheet } from 'react-native'
import React, { useEffect, useState } from 'react'
import { ButtonText, Card, Heading, HStack, ScrollView, Text, Button, Center, Icon, AddIcon, EditIcon, VStack, Divider, Box, Input, InputField, InputSlot, InputIcon, SearchIcon } from '@gluestack-ui/themed'
import { AIRCRAFT_CREATE_ROUTE, REQUEST_CREATE_ROUTE, REQUEST_DETAILS_ROUTE } from '../../Screens'
import { getAllAircraftsRequest } from '../../../../api/new/aircraft/get_all_aircrafts'
import { BoltIcon, Construction, ConstructionIcon, HardHat, Plane } from 'lucide-react-native'
import { getAllServiceRequests } from '../../../../api/new/service_request/get_all_service_requests'
import { TouchableOpacity } from 'react-native'

export const REQUEST_CREATED = "CREATED"
export const REQUEST_IN_PROGRESS = "IN_PROGRESS"
export const REQUEST_COMPLETED = "COMPLETED"
export const REQUEST_INCIDENT = "INCIDENT"

const RequestsListScreen = ({ navigation }) => {
  var [requestsList, setRequestsList] = useState(null)
  var [searchResult, setSearchResult] = useState(null)
  var [searchQuery, setSearchQuery] = useState("")

  navigation.addListener('focus', () => {
      loadServiceRequests()
  });

  const loadServiceRequests = () => {
    getAllServiceRequests({
      onSuccess: (data) => {
        setRequestsList(data)
      }
    })
  }

  const onAddClick = () => {
    console.log("ON_ADD")
    navigation.navigate(REQUEST_CREATE_ROUTE)
  }

  const onPressRequest = (serviceRequest) => {
    navigation.navigate(REQUEST_DETAILS_ROUTE, { requestId: serviceRequest.id })
  }

  useEffect(() => {
    loadServiceRequests()
  }, [])

  useEffect(() => {
    if (requestsList != null) {
      //console.log(aircraftsList)
      const filtered = requestsList.filter(item =>
        ('' + item.id).includes(searchQuery)
      )
      //console.log(filtered)
      setSearchResult(filtered)
    }
  }, [requestsList, searchQuery])

  return (
    <ScrollView>
      <Center p="$10">
        <Card w="100%" h="100%">
          <HStack justifyContent='space-between'>
            <Heading>Заявки на техническое обслуживание</Heading>
            <HStack>
              <Input variant='rounded' mr="$5">
                <InputSlot p="$3">
                  <InputIcon as={SearchIcon} />
                </InputSlot>
                <InputField value={searchQuery} onChangeText={setSearchQuery} placeholder='Номер заявки' />
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
                return <RequestListItem
                  data={item}
                  onAction={() => { }}
                  onPress={onPressRequest.bind(null, item)}
                />
              }
            }
            keyExtractor={item => item.id}
          />
        </Card>
      </Center>
    </ScrollView>
  )
}

const RequestListItem = ({ data, onAction, onPress }) => {
  var statusText = ""
  var bgColor = ""
  var buttonAction = ""
  var buttonTExt = ""
  var showButton = true
  switch (data.status) {
    case REQUEST_CREATED:
      statusText = "СОЗДАНА"
      buttonAction = "positive"
      buttonTExt = "Выдать инструменты"
      bgColor = "blue"; break;
    case REQUEST_IN_PROGRESS: statusText = "В РАБОТЕ";
      buttonAction = "positive"
      buttonTExt = "Начать приемку инструментов"
      bgColor = "orange"; break;
    case REQUEST_COMPLETED: statusText = "ЗАВЕРШЕНА";
      buttonAction = "positive"
      buttonTExt = ""
      bgColor = "green"; showButton = false; break;
    case REQUEST_INCIDENT: statusText = "ИНЦИДЕНТ";
      buttonAction = "neagtive"
      buttonTExt = "Перейти к инциденту"
      bgColor = "red"; break;
  }

  return (
    <VStack space="$2" mb="$2">
      <TouchableOpacity onPress={onPress}>
        <HStack justifyContent='space-between' alignItems='center' mb="$2">
          <HStack>
            <Box h="$20" w="$5" bgColor={bgColor} />
            <VStack pl="$5">
              <Icon as={BoltIcon} size='lg' />
              <Text bold={true} size='lg' >{data.id}</Text>
              <Text size='md'>{"Заявка №" + data.id}</Text>
            </VStack>
          </HStack>


          <VStack space="md">
            <RequestStatusBadge status={data.status}/>
            {showButton ?
              <Button action={buttonAction} onPress={onAction}>
                <ButtonText >{buttonTExt}</ButtonText>
              </Button> : <></>
            }
          </VStack>
        </HStack>
      </TouchableOpacity>
      <Divider />
    </VStack>

  )
}

export const RequestStatusBadge = ({status}) => {
  var statusText = ""
  var bgColor = ""
  switch (status) {
    case REQUEST_CREATED:
      statusText = "СОЗДАНА"
      bgColor = "blue"; break;
    case REQUEST_IN_PROGRESS: statusText = "В РАБОТЕ";
      bgColor = "orange"; break;
    case REQUEST_COMPLETED: statusText = "ЗАВЕРШЕНА";
      bgColor = "green"; break;
    case REQUEST_INCIDENT: statusText = "ИНЦИДЕНТ";
      bgColor = "red"; break;
  }
  return (
    <HStack p="$2" borderRadius="10px" bgColor={bgColor} >
      <Text bold={true} size='lg' color="white" >{statusText}</Text>
    </HStack>
  )
}

export default RequestsListScreen

const styles = StyleSheet.create({})