import { createNativeStackNavigator } from '@react-navigation/native-stack'
import { StyleSheet } from 'react-native'
import { TOOLKIT_CREATE_ROUTE, TOOLKIT_LIST_ROUTE } from '../../Screens'
import ToolkitCreateScreen from './ToolkitCreateScreen'
import ToolkitListScreen from './ToolkitListScreen'

export const ToolkitStack = createNativeStackNavigator()

const ToolkitNavigation = () => {
    return (
        <ToolkitStack.Navigator initialRouteName={TOOLKIT_LIST_ROUTE}>
            <ToolkitStack.Screen
                name={TOOLKIT_LIST_ROUTE}
                component={ToolkitListScreen}
                options={{headerShown: false}}
            />
            <ToolkitStack.Screen
                name={TOOLKIT_CREATE_ROUTE}
                component={ToolkitCreateScreen}
                options={{headerShown: false}}
            />
        </ToolkitStack.Navigator>
    )
}

export default ToolkitNavigation

const styles = StyleSheet.create({})