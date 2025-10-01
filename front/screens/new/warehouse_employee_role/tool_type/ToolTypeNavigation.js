import { StyleSheet, Text, View } from 'react-native'
import React from 'react'
import { TOOL_TYPE_CREATE_ROUTE, TOOL_TYPE_LIST_ROUTE, TOOLKIT_LIST_ROUTE } from '../../Screens'
import ToolTypeListScreen from './ToolTypeListScreen'
import ToolTypeCreateScreen from './ToolTypeCreateScreen'
import { createNativeStackNavigator } from '@react-navigation/native-stack'

export const ToolTypeStack = createNativeStackNavigator()

const ToolTypeNavigation = () => {
    return (
        <ToolTypeStack.Navigator initialRouteName={TOOL_TYPE_LIST_ROUTE}>
            <ToolTypeStack.Screen
                name={TOOLKIT_LIST_ROUTE}
                component={ToolTypeListScreen}
                options={{headerShown: false}}
            />
            <ToolTypeStack.Screen
                name={TOOL_TYPE_CREATE_ROUTE}
                component={ToolTypeCreateScreen}
                options={{headerShown: false}}
            />
        </ToolTypeStack.Navigator>
    )
}

export default ToolTypeNavigation

const styles = StyleSheet.create({})