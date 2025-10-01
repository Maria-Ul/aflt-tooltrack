import { StyleSheet } from 'react-native'
import React, { useCallback, useEffect, useState } from 'react'
import { Box, Button, ButtonText, Card, Center, Heading, Input, InputField, Text, VStack } from '@gluestack-ui/themed'
import WhiteCard from '../../../components/WhiteCard'
import { TOOLS_SCANNER_ROUTE } from '../Screens'
import { getAllServiceRequests } from '../../../api/new/service_request/get_all_service_requests'
import { getAllUsersRequest } from '../../../api/new/users/get_all_users'
import { WORKER_ROLE } from '../../../api/new/register'
import { getRequestWithRelations } from '../../../api/new/service_request/get_request_with_relations'
import { REQUEST_IN_PROGRESS } from '../warehouse_employee_role/maintainance_request/RequestsListScreen'

const EmployeeNumberScreen = ({ navigation }) => {
  var [tabNum, setTabNum] = useState("")
  var [isNextEnabled, setIsNextEnabled] = useState(false)

  var [usersList, setUsersList] = useState([])

  const loadUsers = () => {
    getAllUsersRequest({
      onSuccess: (data) => { setUsersList(data) }
    })
  }

  useEffect(() => {
    loadUsers()
  }, [])

  const loadRequestByWorkerId = (workerId) => {
    console.log("load")
    getAllServiceRequests({
      workerId: workerId,
      onSuccess: (serviceRequestsList) => {
        console.log("GET_ALL_REQUESTS", serviceRequestsList)
        var requestInProgerss = serviceRequestsList.find(r => r.status != "")//== REQUEST_IN_PROGRESS)
        console.log("ONE_REQUEST", requestInProgerss)
        if (requestInProgerss != null) {
          getRequestWithRelations({
            request_id: requestInProgerss.id,
            onSuccess: (requestWithRelations) => {
              console.log("GET_REQUEST_WITH_RELATION", requestWithRelations)
              navigation.navigate(TOOLS_SCANNER_ROUTE, { requestWithRelations: requestWithRelations })
            }
          })
        }

      },
      onError: () => { }
    })
  }

  const onEnterTabNumber = useCallback(() => {
    const currentWorker = usersList.find(u => u.role == WORKER_ROLE && u.tab_number == tabNum)
    loadRequestByWorkerId(currentWorker.id)
  }, [tabNum, usersList])

  const onTabNumChanged = (text) => {
    setTabNum(text)
    setIsNextEnabled(text.length >= 6)
  }

  return (
    <Box>
      <Center m='$16'>
        <Card>
          <VStack alignItems='center'>
            <Heading mb='$10'>Прием/выдача инструментов</Heading>
            <Text mb='$3'>Табельный номер</Text>
            <Input mb='$6'>
              <InputField value={tabNum} onChangeText={onTabNumChanged} placeholder="Введите номер" />
            </Input>
            <Button onPress={onEnterTabNumber} isDisabled={!isNextEnabled}>
              <ButtonText>Продолжить</ButtonText>
            </Button>
          </VStack>
        </Card>
      </Center>
    </Box>
  )
}

export default EmployeeNumberScreen

const styles = StyleSheet.create({})