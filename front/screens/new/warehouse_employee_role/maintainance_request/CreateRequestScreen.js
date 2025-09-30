import { Button, ButtonText, Card, Text, Center, Heading, HStack, Input, InputField, Select, SelectItem, VStack, Icon, ChevronLeftIcon, SelectTrigger, SelectInput, SelectIcon, SelectPortal, SelectContent, SelectDragIndicator, ChevronDownIcon } from '@gluestack-ui/themed'
import { useCallback, useEffect, useState } from 'react'
import { StyleSheet } from 'react-native'
import { getAllAircraftsRequest } from '../../../../api/new/aircraft/get_all_aircrafts'
import { WAREHOUSE_EMPLOYEE_ROLE, WORKER_ROLE } from '../../../../api/new/register'
import { createServiceRequest } from '../../../../api/new/service_request/create_service_request'
import { getAllToolkits } from '../../../../api/new/tool_sets/get_all_tool_sets'
import { getAllUsersRequest } from '../../../../api/new/users/get_all_users'
import { REQUEST_COMPLETED, REQUEST_CREATED, REQUEST_IN_PROGRESS, REQUEST_INCIDENT } from './RequestsListScreen'
import { SelectBackdrop } from '@gluestack-ui/themed'
import { SelectDragIndicatorWrapper } from '@gluestack-ui/themed'

const CreateRequestScreen = ({ navigation }) => {
    var [selectedAircraft, setSelectedAircraft] = useState(null)
    var [selectedWorker, setSelectedWorker] = useState(null)
    var [selectedWarehouseEmployee, setSelectedWarehouseEmployee] = useState(null)
    var [selectedToolkit, setSelectedToolkit] = useState(null)
    var [description, setDescription] = useState("")

    var [aircraftsList, setAircraftsList] = useState([])
    var [workersList, setWorkersLsit] = useState([])
    var [warehouseEmployeesList, setWarehouseEmployeesList] = useState([])
    var [toolkitList, setToolkitList] = useState([])

    useEffect(() => {
        getAllUsersRequest({
            onSuccess: (users) => {
                setWorkersLsit(users.filter(user => user.role == WORKER_ROLE))
                setWarehouseEmployeesList(users.filter(user => user.role == WAREHOUSE_EMPLOYEE_ROLE))
            }
        })
    }, [])

    useEffect(() => {
        getAllToolkits({
            onSuccess: (toolkits) => {
                setToolkitList(toolkits)
            }
        })
    }, [])

    useEffect(() => {
        getAllAircraftsRequest({
            onSuccess: (aircrafts) => {
                setAircraftsList(aircrafts)
            }
        })
    },[])


    var isAddEnabled = selectedAircraft != null && selectedToolkit != null &&
        selectedWarehouseEmployee != null && selectedWorker != null

    const onAddClick = useCallback(() => {
        console.log("ADD")
        console.log(selectedAircraft)
        
        createServiceRequest({
            aircraft_id: selectedAircraft,
            aviation_engineer_id: selectedWorker,
            tool_set_id: selectedToolkit,
            warehouse_employee_id: selectedWarehouseEmployee,
            description: description,
            status: REQUEST_COMPLETED,
            onSuccess: () => {
                navigation.goBack()
            }
        })
    }, [selectedAircraft, selectedToolkit, selectedWarehouseEmployee, selectedWorker, description])

    const onBackPressed = () => {
        navigation.goBack()
    }

    return (
        <Center>
            <Card m="$10">
                <VStack space="md" p="$5">
                    <HStack alignItems='center' mb="$3">
                        <Button onPress={onBackPressed} mr="$5">
                            <Icon as={ChevronLeftIcon} color="white" />
                        </Button>
                        <Heading>Добавить заявку на техническое обслуживание</Heading>
                    </HStack>

                    <Text>Воздушное судно для обслуживания</Text>
                    <EntitySelector
                        entities={aircraftsList}
                        entityType={AIRCRAFT_ENTITY}
                        value={selectedAircraft}
                        onSelectEntity={setSelectedAircraft}
                        placeholder={"Выберите воздушное судно для обслуживания"} />

                    <Text>Исполнитель работ</Text>
                    <EntitySelector
                        entities={workersList}
                        entityType={USER_ENTITY}
                        value={selectedWorker}
                        onSelectEntity={setSelectedWorker}
                        placeholder={"Выберите исполнителя работ"} />

                    <Text>Ответственный сотрудник склада</Text>
                    <EntitySelector
                        entities={warehouseEmployeesList}
                        entityType={USER_ENTITY}
                        value={selectedWarehouseEmployee}
                        onSelectEntity={setSelectedWarehouseEmployee}
                        placeholder={"Выберите ответственного сотрудника склада"} />

                    <Text>Набор инструментов</Text>
                    <EntitySelector
                        entities={toolkitList}
                        entityType={TOOLKIT_ENTITY}
                        value={selectedToolkit}
                        onSelectEntity={setSelectedToolkit}
                        placeholder={"Выберите набор инструментов"} />

                    <Text>Описание</Text>
                    <Input>
                        <InputField value={description} onChangeText={setDescription} placeholder="Описание" />
                    </Input>
                    <HStack space="md">
                        <Button onPress={onAddClick} disabled={!isAddEnabled}>
                            <ButtonText>Добавить</ButtonText>
                        </Button>
                    </HStack>
                </VStack>
            </Card>
        </Center>
    )
}

const AIRCRAFT_ENTITY = "a"
const USER_ENTITY = "u"
const TOOLKIT_ENTITY = "t"

const EntitySelector = ({
    entities,
    entityType,
    value,
    onSelectEntity,
    placeholder,
}) => {
    const selectorItems = entities.map(entity => {
        var label = ""
        switch (entityType) {
            case AIRCRAFT_ENTITY: label = entity.tail_number + " " + entity.model; break;
            case USER_ENTITY: label = entity.tab_number + " " + entity.full_name; break;
            case TOOLKIT_ENTITY: label = entity.batch_number + " " + entity.description; break;
        }
        return (
            <SelectItem label={label} value={entity.id} />
        )
    })
    return (
        <Select selectedValue={value} onValueChange={onSelectEntity}>
            <SelectTrigger size="md">
                <SelectInput width="500px" placeholder={placeholder} />
                <SelectIcon className="mr-3" as={ChevronDownIcon} />
            </SelectTrigger>
            <SelectPortal>
                <SelectBackdrop />
                <SelectContent>
                    <SelectDragIndicatorWrapper>
                        <SelectDragIndicator />
                    </SelectDragIndicatorWrapper>
                    {selectorItems}
                    {/* <SelectItem label="UX Research" value="ux" />
                                        <SelectItem label="Web Development" value="web" />
                                        <SelectItem
                                            label="Cross Platform Development Process"
                                            value="Cross Platform Development Process"
                                        />
                                        <SelectItem label="UI Designing" value="ui" isDisabled={true} />
                                        <SelectItem label="Backend Development" value="backend" /> */}
                </SelectContent>
            </SelectPortal>
        </Select>
    )
}

export default CreateRequestScreen

const styles = StyleSheet.create({})