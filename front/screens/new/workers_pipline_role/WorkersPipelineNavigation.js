import { StyleSheet, Text, View } from 'react-native'
import React from 'react'
import { createNativeStackNavigator } from '@react-navigation/native-stack'
import { SERVICE_NAME } from '../../../App'
import { headerLeft, headerRight, headerStyle } from '../AppHeader'
import { EMPLOYEE_NUMBER_ROUTE, NO_REQUESTS_ROUTE, TOOLS_SCANNER_ROUTE } from '../Screens'
import NoRequestsScreen from './NoRequestsScreen'
import EmployeeNumberScreen from './EmployeeNumberScreen'
import ToolsScanerScreen from './tool_scanner/ToolsScanerScreen'

const WorkersPipelineStack = createNativeStackNavigator()

const WorkersPipelineNavigation = () => {
    return (
        <WorkersPipelineStack.Navigator>
            <WorkersPipelineStack.Screen
                name={TOOLS_SCANNER_ROUTE}
                component={ToolsScanerScreen}
                options={{headerShown:false}}
            />
            <WorkersPipelineStack.Screen
                name={NO_REQUESTS_ROUTE}
                component={NoRequestsScreen}
                options={{headerShown:false}}
            />
            <WorkersPipelineStack.Screen
                name={EMPLOYEE_NUMBER_ROUTE}
                component={EmployeeNumberScreen}
                options={{headerShown:false}}
            />
        </WorkersPipelineStack.Navigator>
    )
}

export default WorkersPipelineNavigation

const styles = StyleSheet.create({})