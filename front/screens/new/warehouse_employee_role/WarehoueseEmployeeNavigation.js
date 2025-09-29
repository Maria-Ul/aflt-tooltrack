import { createDrawerNavigator } from '@react-navigation/drawer'
import { StyleSheet } from 'react-native'
import { headerLeft, headerRight, headerStyle } from '../AppHeader'
import { AIRCRAFT_ROUTE, REQUESTS_ROUTE, TOOL_TYPE_ROUTE, TOOLKIT_ROUTE, TOOLKIT_TYPE_ROUTE } from '../Screens'
import AircraftNavigation from './aircraft/AircraftNavigation'
import RequestsListScreen from './maintainance_request/RequestsListScreen'
import ToolTypeNavigation from './tool_type/ToolTypeNavigation'
import ToolkitListScreen from './toolkit/ToolkitListScreen'
import ToolkitTypeNavigation from './toolkit_type/ToolkitTypeNavigation'

export const WarehouseEmployeeRoleDrawer = createDrawerNavigator()

const WarehoueseEmployeeNavigation = () => {
    return (
        <WarehouseEmployeeRoleDrawer.Navigator initialRouteName={AIRCRAFT_ROUTE}>
            <WarehouseEmployeeRoleDrawer.Screen
                name={REQUESTS_ROUTE}
                component={RequestsListScreen}
                options={{
                    headerStyle: headerStyle,
                    headerRight: headerRight,
                    headerTitle: headerLeft,
                }}
            />
            <WarehouseEmployeeRoleDrawer.Screen
                name={AIRCRAFT_ROUTE}
                component={AircraftNavigation}
                options={{
                    headerStyle: headerStyle,
                    headerRight: headerRight,
                    headerTitle: headerLeft,
                    headerTitle: headerLeft,
                }}
            />
            <WarehouseEmployeeRoleDrawer.Screen
                name={TOOLKIT_ROUTE}
                component={ToolkitListScreen}
                options={{
                    headerStyle: headerStyle,
                    headerRight: headerRight,
                    headerTitle: headerLeft,
                }}
            />
            <WarehouseEmployeeRoleDrawer.Screen
                name={TOOLKIT_TYPE_ROUTE}
                component={ToolkitTypeNavigation}
                options={{
                    headerStyle: headerStyle,
                    headerRight: headerRight,
                    headerTitle: headerLeft,
                }}
            />
            <WarehouseEmployeeRoleDrawer.Screen
                name={TOOL_TYPE_ROUTE}
                component={ToolTypeNavigation}
                options={{
                    headerStyle: headerStyle,
                    headerRight: headerRight,
                    headerTitle: headerLeft,
                }}
            />
        </WarehouseEmployeeRoleDrawer.Navigator>
    )
}

export default WarehoueseEmployeeNavigation

const styles = StyleSheet.create({})