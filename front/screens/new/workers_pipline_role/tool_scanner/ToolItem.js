import { StyleSheet } from 'react-native'
import React from 'react'
import { CheckIcon, CloseIcon, HStack, Icon, Text, View, VStack } from '@gluestack-ui/themed'

const ToolItem = ({
    name,
    probability,
    threshold,
}) => {
    var successRecognition = probability > threshold
    return (
        <HStack p='$3' mb='$1' style={styles.tool_item_container} alignItems='center' alignContent='space-between'>
            <VStack mr='$10'>
                <Text size='lg'>{name}</Text>
                {
                    successRecognition ?
                        <View /> : <Text size='xs' color='orange'>
                            Не удается точно определить инструмент
                        </Text>
                }

            </VStack>
            <HStack>
                <Text size='lg' bold={true}>{probability * 100}%</Text>
                <Icon as={successRecognition ? CheckIcon : CloseIcon} size='xl'
                    color={successRecognition ? 'green' : "red"} />
            </HStack>
        </HStack>
    )
}

export default ToolItem

const styles = StyleSheet.create({
    tool_item_container: {
        borderColor: '#dddddd',
        borderWidth: 2,
        borderRadius: 10,
        borderStyle: 'solid',
    }
})