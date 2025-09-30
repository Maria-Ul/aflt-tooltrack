import { StyleSheet } from 'react-native'
import React, { useState } from 'react'
import { Box, Button, ButtonText, Card, Center, Heading, Input, InputField, Text, VStack } from '@gluestack-ui/themed'
import WhiteCard from '../../../components/WhiteCard'
import { TOOLS_SCANNER_ROUTE } from '../Screens'

const EmployeeNumberScreen = ({ navigation }) => {
  var [tabNum, setTabNum] = useState("")
  var [isNextEnabled, setIsNextEnabled] = useState(false)

  const loadRequestByWorkerTabNum = (tabNumber) => {
    
  }

  const onContinue = () => {
      navigation.navigate(TOOLS_SCANNER_ROUTE)
  } 

  const onTabNumChanged = (text) => {
    setTabNum(text)
    setIsNextEnabled(text.length >= 6)
  }

  return (
    <Box>
      <Center m='$16'>
        <Card>
          <VStack alignItems='center'>
            <Heading mb='$10'>Прием/выдача инструментов</Heading>
            <Text mb='$3'>Табельный номер</Text>
            <Input mb='$6'>
              <InputField value={tabNum} onChangeText={onTabNumChanged} placeholder="Введите номер" />
            </Input>
            <Button onPress={onContinue} isDisabled={!isNextEnabled}>
              <ButtonText>Продолжить</ButtonText>
            </Button>
          </VStack>
        </Card>
      </Center>
    </Box>
  )
}

export default EmployeeNumberScreen

const styles = StyleSheet.create({})