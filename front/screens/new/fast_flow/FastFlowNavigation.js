import { StyleSheet, Text, View } from 'react-native'
import React from 'react'
import { createNativeStackNavigator } from '@react-navigation/native-stack'
import { EMPLOYEE_NUMBER_ROUTE, FAST_FLOW_SCREEN_ROUTE, } from '../Screens'
import FastToolsScanerScreen from './tool_scanner/FastToolsScanerScreen'

const FastFlowStack = createNativeStackNavigator()

const FastFlowNavigation = () => {
    return (
        <FastFlowStack.Navigator initialRouteName={EMPLOYEE_NUMBER_ROUTE}>
            <FastFlowStack.Screen
                name={FAST_FLOW_SCREEN_ROUTE}
                component={FastToolsScanerScreen}
                options={{headerShown:false}}
            />
        </FastFlowStack.Navigator>
    )
}

export default FastFlowNavigation

const styles = StyleSheet.create({})