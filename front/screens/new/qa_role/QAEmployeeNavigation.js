import { createNativeStackNavigator } from '@react-navigation/native-stack'
import { StyleSheet } from 'react-native'
import { INCIDENT_DETAILS_ROUTE, INCIDENT_LIST_ROUTE } from '../Screens'
import IncidentDetailsScreen from './IncidentDetailsScreen'
import IncidentsListScreen from './IncidentListScreen'

export const QAEmployeeStack = createNativeStackNavigator()

const QAEmployeeNavigation = () => {
    return (
        <QAEmployeeStack.Navigator initialRouteName={INCIDENT_LIST_ROUTE}>
            <QAEmployeeStack.Screen
                name={INCIDENT_LIST_ROUTE}
                component={IncidentsListScreen}
                options={{headerShown: false}}
            />
            <QAEmployeeStack.Screen
                name={INCIDENT_DETAILS_ROUTE}
                component={IncidentDetailsScreen}
                options={{headerShown: false}}
            />
        </QAEmployeeStack.Navigator>
    )
}

export default QAEmployeeNavigation

const styles = StyleSheet.create({})