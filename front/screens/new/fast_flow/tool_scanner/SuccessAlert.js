import { StyleSheet, Text, View } from 'react-native'
import React from 'react'

const SuccessAlert = ({ style }) => {
    return (
        <HStack style={style} p="$3" space='md' bgColor='#94f794ff'
            borderWidth="2px" borderColor='#2fff00ff' alignItems='center'>
            <Icon as={CheckIcon} size='xl' />
            <Text size="lg" bold="true">{`Все инструменты из набора распознаны\nМожно завершить приемку`}</Text>
        </HStack>
    )
}

export default SuccessAlert

const styles = StyleSheet.create({})