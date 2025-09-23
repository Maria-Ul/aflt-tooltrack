import { StyleSheet, Text, View } from 'react-native'
import React from 'react'
import { createDrawerNavigator } from '@react-navigation/drawer'
import { AIRCRAFT_CREATE, AIRCRAFT_LIST, EMPLOYEE_NUMBER_ROUTE, KIT_LIST, REQUESTS_LIST, TEMPLATE_KIT_LIST, TEMPLATE_TOOL_LIST } from '../Screens'
import RequestsListScreen from './RequestsListScreen'
import AircraftListScreen from './AircraftListScreen'
import KitListScreen from './KitListScreen'
import TemplateKitListScreen from './TemplateKitListScreen'
import TemplateToolListScreen from './TemplateToolListScreen'

export const WarehouseEmployeeRoleDrawer = createDrawerNavigator()

const WarehoueseEmployeeNavigation = () => {
    return (
        <WarehouseEmployeeRoleDrawer.Navigator>
            <WarehouseEmployeeRoleDrawer.Screen
                name={REQUESTS_LIST}
                component={RequestsListScreen}
            />
            <WarehouseEmployeeRoleDrawer.Screen
                name={AIRCRAFT_LIST}
                component={AircraftListScreen}
            />
            <WarehouseEmployeeRoleDrawer.Screen
                name={KIT_LIST}
                component={KitListScreen}
            />
            <WarehouseEmployeeRoleDrawer.Screen
                name={TEMPLATE_KIT_LIST}
                component={TemplateKitListScreen}
            />
            <WarehouseEmployeeRoleDrawer.Screen
                name={TEMPLATE_TOOL_LIST}
                component={TemplateToolListScreen}
            />
        </WarehouseEmployeeRoleDrawer.Navigator>
    )
}

export default WarehoueseEmployeeNavigation

const styles = StyleSheet.create({})