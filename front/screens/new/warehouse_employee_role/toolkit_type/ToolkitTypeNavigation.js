import { createNativeStackNavigator } from '@react-navigation/native-stack'
import { StyleSheet } from 'react-native'
import { TOOLKIT_TYPE_CREATE_ROUTE, TOOLKIT_TYPE_LIST_ROUTE } from '../../Screens'
import ToolkitTypeCreateScreen from './ToolkitTypeCreateScreen'
import ToolkitTypeListScreen from './ToolkitTypeListScreen'

export const ToolkitTypeStack = createNativeStackNavigator()

const ToolkitTypeNavigation = () => {
    return (
        <ToolkitTypeStack.Navigator initialRouteName={TOOLKIT_TYPE_LIST_ROUTE}>
            <ToolkitTypeStack.Screen
                name={TOOLKIT_TYPE_LIST_ROUTE}
                component={ToolkitTypeListScreen}
                options={{headerShown: false}}
            />
            <ToolkitTypeStack.Screen
                name={TOOLKIT_TYPE_CREATE_ROUTE}
                component={ToolkitTypeCreateScreen}
                options={{headerShown: false}}
            />
        </ToolkitTypeStack.Navigator>
    )
}

export default ToolkitTypeNavigation

const styles = StyleSheet.create({})