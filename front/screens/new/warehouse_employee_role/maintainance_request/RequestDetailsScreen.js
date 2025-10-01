import { Button, ButtonText, Card, Text, Center, Heading, HStack, Input, InputField, Select, SelectItem, VStack, Icon, ChevronLeftIcon, SelectTrigger, SelectInput, SelectIcon, SelectPortal, SelectContent, SelectDragIndicator, ChevronDownIcon } from '@gluestack-ui/themed'
import { useCallback, useEffect, useState } from 'react'
import { StyleSheet } from 'react-native'
import { getAllAircraftsRequest } from '../../../../api/new/aircraft/get_all_aircrafts'
import { WAREHOUSE_EMPLOYEE_ROLE, WORKER_ROLE } from '../../../../api/new/register'
import { createServiceRequest } from '../../../../api/new/service_request/create_service_request'
import { getAllToolkits } from '../../../../api/new/tool_sets/get_all_tool_sets'
import { getAllUsersRequest } from '../../../../api/new/users/get_all_users'
import { REQUEST_COMPLETED, REQUEST_CREATED, REQUEST_IN_PROGRESS, REQUEST_INCIDENT, RequestStatusBadge } from './RequestsListScreen'
import { SelectBackdrop } from '@gluestack-ui/themed'
import { SelectDragIndicatorWrapper } from '@gluestack-ui/themed'
import { getRequestWithRelations } from '../../../../api/new/service_request/get_request_with_relations'

const RequestDetailsScreen = ({ route, navigation }) => {
    const { requestId } = route.params

    var [requestWithRelations, setRequestWithRelations] = useState(null)

    const loadRequestWithRelations = () => {
        getRequestWithRelations({
            request_id: requestId,
            onSuccess: (data) => {
                setRequestWithRelations(data)
            }
        })
    }

    useEffect(() => {
        loadRequestWithRelations()
    }, [])

    const onBackPressed = () => {
        navigation.goBack()
    }

    return (
        <Center p="$10">
            <Card w="100%" h="100%">
                {
                    requestWithRelations != null ?
                        <HStack justifyContent='space-between'>
                            <VStack space="md" p="$5">
                                <HStack alignItems='center' mb="$3">
                                    <Button onPress={onBackPressed} mr="$5">
                                        <Icon as={ChevronLeftIcon} color="white" />
                                    </Button>
                                    <Heading>{`Заявка №${requestWithRelations.id ?? ""}`}</Heading>
                                </HStack>

                                <Text size='lg'  bold={true}>Воздушное судно для обслуживания:</Text>
                                <Text>{`${requestWithRelations.aircraft.tail_number} ${requestWithRelations.aircraft.model}`}</Text>


                                <Text size='lg'  bold={true}>Ответственный сотрудник склада:</Text>
                                <Text>{`${requestWithRelations.warehouse_employee.tab_number} ${requestWithRelations.warehouse_employee.full_name}`}</Text>


                                <Text size='lg'  bold={true}>Набор инструментов:</Text>
                                <Text>{`${requestWithRelations.tool_set.batch_number}`}</Text>


                                <Text size='lg'  bold={true}>Описание:</Text>
                                <Text>{`${requestWithRelations.description}`}</Text>

                                <Text size='lg'  bold={true}>Инцидент:</Text>

                            </VStack>
                            <VStack p="$5" space='md'>
                                <Text size='lg' bold={true}>Исполнитель работ:</Text>
                                <Text>{`${requestWithRelations.aviation_engineer.tab_number} ${requestWithRelations.aviation_engineer.full_name}`}</Text>
                                <Text size='lg'  bold={true}>Статус:</Text>
                                <RequestStatusBadge status={requestWithRelations.status}/>
                            </VStack>
                        </HStack>

                        : <></>
                }
            </Card>
        </Center>
    )
}
export default RequestDetailsScreen

const styles = StyleSheet.create({})