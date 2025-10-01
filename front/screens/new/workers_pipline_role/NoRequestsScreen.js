import { StyleSheet, Text, View } from 'react-native'
import React from 'react'
import { Box, Button, ButtonText, Card, Center, VStack } from '@gluestack-ui/themed'
import WhiteCard from '../../../components/WhiteCard'

const NoRequestsScreen = ({ navigation }) => {
  return (
    <Box>
      <Center>
        <Card>
          <VStack alignItems='center'>
            <Text>Нет активных заявок на техническое обслуживание</Text>
            <Text>Обратитесь к сотруднику склада</Text>
            <Button>
              <ButtonText>Выход</ButtonText>
            </Button>
          </VStack>
        </Card>
      </Center>
    </Box>
  )
}

export default NoRequestsScreen

const styles = StyleSheet.create({})