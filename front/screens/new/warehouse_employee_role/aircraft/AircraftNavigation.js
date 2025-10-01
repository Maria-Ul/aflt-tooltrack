import { StyleSheet, Text, View } from 'react-native'
import { createNativeStackNavigator } from '@react-navigation/native-stack'
import { AIRCRAFT_CREATE_ROUTE, AIRCRAFT_DETAILS_ROUTE, AIRCRAFT_LIST_ROUTE } from '../../Screens'
import AircraftCreateScreen from './AircraftCreateScreen'
import AircraftListScreen from './AircraftListScreen'
import AircraftDetailsScreen from './AircraftDetailsScreen'

export const AircraftStack = createNativeStackNavigator()

const AircraftNavigation = () => {
    return (
        <AircraftStack.Navigator initialRouteName={AIRCRAFT_LIST_ROUTE}>
            <AircraftStack.Screen
                name={AIRCRAFT_LIST_ROUTE}
                component={AircraftListScreen}
                options={{headerShown: false}}
            />
            <AircraftStack.Screen
                name={AIRCRAFT_CREATE_ROUTE}
                component={AircraftCreateScreen}
                options={{headerShown: false}}
            />
            <AircraftStack.Screen
                name={AIRCRAFT_DETAILS_ROUTE}
                component={AircraftDetailsScreen}
                options={{headerShown: false}}
            />
        </AircraftStack.Navigator>
    )
}

export default AircraftNavigation

const styles = StyleSheet.create({})