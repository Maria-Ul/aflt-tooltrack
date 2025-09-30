import { Box, Card, Center, Divider, Heading, HStack, Icon, Input, InputField, InputIcon, InputSlot, ScrollView, SearchIcon, Text, VStack } from '@gluestack-ui/themed'
import { BoltIcon } from 'lucide-react-native'
import { useEffect, useState } from 'react'
import { FlatList, StyleSheet, TouchableOpacity } from 'react-native'
import { getAllIncidentsRequest, getAllIncidentsRequeszt } from '../../../api/new/incident/get_all_incidents'
import { INCIDENT_DETAILS_ROUTE } from '../Screens'

export const INCIDENT_OPEN = "OPEN"
export const INCIDENT_INVESTIGATING = "INVESTIGATING"
export const INCIDENT_RESOLVED = "RESOLVED"
export const INCIDENT_CLOSED = "CLOSED"

const IncidentsListScreen = ({ navigation }) => {
    var [incidentsList, setIncidentsList] = useState([])
    var [searchResult, setSearchResult] = useState([])
    var [searchQuery, setSearchQuery] = useState("")
    var [selectedIncidentStatus, setIncidentStatus] = useState("")

    const loadIncidents = () => {
        getAllIncidentsRequest({
            onSuccess: (data) => {
                setIncidentsList(data)
            }
        })
    }

    const onPressIncident = (incident) => {
        navigation.navigate(INCIDENT_DETAILS_ROUTE, { incidentId: incident.id })
    }

    useEffect(() => {
        loadIncidents()
    }, [])

    useEffect(() => {
        if (incidentsList != null) {
            //console.log(aircraftsList)
            const filtered = incidentsList.filter(item =>
                ('' + item.id).includes(searchQuery) && item.status.includes(selectedIncidentStatus)
            )
            //console.log(filtered)
            setSearchResult(filtered)
        }
    }, [incidentsList, searchQuery])

    return (
        <ScrollView>
            <Center p="$10">
                <Card w="100%" h="100%">
                    <HStack justifyContent='space-between'>
                        <Heading>Инциденты недостачи</Heading>
                        <HStack>
                            <Input variant='rounded' mr="$5">
                                <InputSlot p="$3">
                                    <InputIcon as={SearchIcon} />
                                </InputSlot>
                                <InputField value={searchQuery} onChangeText={setSearchQuery} placeholder='Номер инцидента' />
                            </Input>
                        </HStack>

                    </HStack>
                    <Divider mt="$5" mb="$5" />
                    {
                        searchResult.length > 0 ?
                            <FlatList
                                data={searchResult}
                                renderItem={
                                    ({ item, index, separators }) => {
                                        return <IncidentListItem
                                            data={item}
                                            onAction={() => { }}
                                            onPress={onPressRequest.bind(null, item)}
                                        />
                                    }
                                }
                                keyExtractor={item => item.id}
                            /> : <></>
                    }

                </Card>
            </Center>
        </ScrollView>
    )
}

const IncidentListItem = ({ data, onPress }) => {
    var bgColor = ""
    switch (data.status) {
        case INCIDENT_OPEN:
            bgColor = "blue"; break;
        case INCIDENT_INVESTIGATING:
            bgColor = "orange"; break;
        case INCIDENT_RESOLVED:
            bgColor = "green"; break;
        case INCIDENT_CLOSED:
            bgColor = "grey"; break;
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
                        <IncidentStatusBadge status={data.status} />
                    </VStack>
                </HStack>
            </TouchableOpacity>
            <Divider />
        </VStack>

    )
}

export const IncidentStatusBadge = ({ status }) => {
    var statusText = ""
    var bgColor = ""
    switch (status) {
        case INCIDENT_OPEN:
            statusText = "ОТКРЫТ"
            bgColor = "blue"; break;
        case INCIDENT_INVESTIGATING: statusText = "РАССЛЕДОВАНИЕ";
            bgColor = "orange"; break;
        case INCIDENT_RESOLVED: statusText = "РЕШЕН";
            bgColor = "green"; break;
        case INCIDENT_CLOSED: statusText = "ЗАКРЫТ";
            bgColor = "grey"; break;
    }
    return (
        <HStack p="$2" borderRadius="10px" bgColor={bgColor} >
            <Text bold={true} size='lg' color="white" >{statusText}</Text>
        </HStack>
    )
}

export default IncidentsListScreen

const styles = StyleSheet.create({})