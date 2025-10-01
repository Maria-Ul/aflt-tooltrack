import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View } from 'react-native';
import { NavigationContainer, useNavigation } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';


import { GluestackUIProvider, } from '@gluestack-ui/themed';
import { config } from "@gluestack-ui/config"
import AuthScreen from './screens/new/AuthScreen';
import { AUTH_SCREEN_ROUTE, QA_EMPLOYEE_ROLE_ROUTE, REGISTRATION_SCREEN_ROUTE, REQUESTS_LIST, TOOLS_SCANNER_ROUTE, USER_GUIDE_ROUTE, WAREHOUSE_EMPLOYEE_ROUTE, WORKERS_PIPELINE_ROLE_ROUTE } from './screens/new/Screens';
import RegistrationScreen from './screens/new/RegistrationScreen';
import applyCustomConfig from './screens/new/ThemeConfig';
import { guideHeaderRight, headerLeft, headerRight, headerStyle, preloginHeaderLeft, preloginHeaderRight } from './screens/new/AppHeader';
import WarehoueseEmployeeNavigation, { WarehouseEmployeeRoleDrawer } from './screens/new/warehouse_employee_role/WarehoueseEmployeeNavigation';
import WorkersPipelineNavigation from './screens/new/workers_pipline_role/WorkersPipelineNavigation';
import UserGuideScreen from './screens/new/UserGuideScreen';
import QAEmployeeNavigation from './screens/new/qa_role/QAEmployeeNavigation';

export const SERVICE_NAME = `Сервис приема и выдачи инструментов`
// TODO панель настроек
export const CONFIDENCE_THRESHOLD = 0.9

export const AppStack = createNativeStackNavigator()

export default function App() {
  applyCustomConfig(config)

  return (
    <GluestackUIProvider config={config}>
      <NavigationContainer>
        <AppStack.Navigator>
          <AppStack.Screen
            name={AUTH_SCREEN_ROUTE}
            component={AuthScreen}
            options={{
              title: SERVICE_NAME,
              headerStyle: headerStyle,
              headerLeft: preloginHeaderLeft,
              headerRight: preloginHeaderRight,
            }} />
          <AppStack.Screen
            name={REGISTRATION_SCREEN_ROUTE}
            component={RegistrationScreen}
            options={{
              title: SERVICE_NAME,
              headerStyle: headerStyle,
              headerLeft: preloginHeaderLeft,
              headerRight: preloginHeaderRight,
            }} />
          <AppStack.Screen
            name={WORKERS_PIPELINE_ROLE_ROUTE}
            component={WorkersPipelineNavigation}
            options={{
              title: SERVICE_NAME,
              headerStyle: headerStyle,
              headerLeft: headerLeft,
              headerRight: headerRight,
            }} />
          <AppStack.Screen
            name={WAREHOUSE_EMPLOYEE_ROUTE}
            component={WarehoueseEmployeeNavigation}
            options={{ headerShown: false }} />
          <AppStack.Screen
            name={USER_GUIDE_ROUTE}
            component={UserGuideScreen}
            options={{
              title: SERVICE_NAME,
              headerStyle: headerStyle,
              headerLeft: preloginHeaderLeft,
              headerRight: guideHeaderRight,
            }}
          />
          <AppStack.Screen
            name={QA_EMPLOYEE_ROLE_ROUTE}
            component={QAEmployeeNavigation}
            options={{
              title: SERVICE_NAME,
              headerStyle: headerStyle,
              headerLeft: headerLeft,
              headerRight: headerRight,
            }}
          />
        </AppStack.Navigator>
      </NavigationContainer>
    </GluestackUIProvider>
  );
}
