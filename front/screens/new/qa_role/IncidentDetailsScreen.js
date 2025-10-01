import { Button, Card, Center, ChevronLeftIcon, Heading, HStack, Icon, Text, VStack } from '@gluestack-ui/themed'
import { useEffect, useState } from 'react'
import { StyleSheet } from 'react-native'
import { getIncidentWithRelations } from '../../../api/new/incident/get_incident_with_relations'
import { IncidentStatusBadge } from './IncidentListScreen'

const IncidentDetailsScreen = ({ route, navigation }) => {
    const { incidentId } = route.params

    var [incidentWithRelations, setIncidentWithRelations] = useState(null)

    const loadIncidentWithRelations = () => {
        getIncidentWithRelations({
            incident_id: incidentId,
            onSuccess: (data) => {
                setШncidentWithRelations(data)
            }
        })
    }

    useEffect(() => {
        loadIncidentWithRelations()
    }, [])

    const onBackPressed = () => {
        navigation.goBack()
    }

    return (
        <Center p="$10">
            <Card w="100%" h="100%">
                {
                    incidentWithRelations != null ?
                        <HStack justifyContent='space-between'>
                            <VStack space="md" p="$5">
                                <HStack alignItems='center' mb="$3">
                                    <Button onPress={onBackPressed} mr="$5">
                                        <Icon as={ChevronLeftIcon} color="white" />
                                    </Button>
                                    <Heading>{`Инцидент №${incidentWithRelations.id}`}</Heading>
                                </HStack>

                                <Text size='lg'  bold={true}>Воздушное судно для обслуживания:</Text>
                                <Text>{`${incidentWithRelations.aircraft.tail_number} ${incidentWithRelations.aircraft.model}`}</Text>


                                <Text size='lg'  bold={true}>Ответственный сотрудник склада:</Text>
                                <Text>{`${incidentWithRelations.warehouse_employee.tab_number} ${incidentWithRelations.warehouse_employee.full_name}`}</Text>


                                <Text size='lg'  bold={true}>Набор инструментов:</Text>
                                <Text>{`${incidentWithRelations.tool_set.batch_number}`}</Text>


                                <Text size='lg'  bold={true}>Описание:</Text>
                                <Text>{`${incidentWithRelations.description}`}</Text>

                                <Text size='lg'  bold={true}>Инцидент:</Text>

                            </VStack>
                            <VStack p="$5" space='md'>
                                <Text size='lg' bold={true}>Исполнитель работ:</Text>
                                <Text>{`${incidentWithRelations.aviation_engineer.tab_number} ${incidentWithRelations.aviation_engineer.full_name}`}</Text>
                                <Text size='lg'  bold={true}>Статус:</Text>
                                <IncidentStatusBadge status={incidentWithRelations.status}/>
                            </VStack>
                        </HStack>

                        : <></>
                }
            </Card>
        </Center>
    )
}
export default IncidentDetailsScreen

const styles = StyleSheet.create({})