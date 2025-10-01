import { createNativeStackNavigator } from '@react-navigation/native-stack'
import { StyleSheet } from 'react-native'
import { REQUEST_CREATE_ROUTE, REQUEST_DETAILS_ROUTE, REQUESTS_LIST_ROUTE } from '../../Screens'
import CreateRequestScreen from './CreateRequestScreen'
import RequestDetailsScreen from './RequestDetailsScreen'
import RequestsListScreen from './RequestsListScreen'

export const ServiceRequestsStack = createNativeStackNavigator()

const ServiceRequestsNavigation = () => {
    return (
        <ServiceRequestsStack.Navigator initialRouteName={REQUESTS_LIST_ROUTE}>
            <ServiceRequestsStack.Screen
                name={REQUESTS_LIST_ROUTE}
                component={RequestsListScreen}
                options={{headerShown: false}}
            />
            <ServiceRequestsStack.Screen
                name={REQUEST_CREATE_ROUTE}
                component={CreateRequestScreen}
                options={{headerShown: false}}
            />
            <ServiceRequestsStack.Screen
                name={REQUEST_DETAILS_ROUTE}
                component={RequestDetailsScreen}
                options={{headerShown: false}}
            />
        </ServiceRequestsStack.Navigator>
    )
}

export default ServiceRequestsNavigation

const styles = StyleSheet.create({})