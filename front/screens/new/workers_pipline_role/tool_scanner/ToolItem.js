import { StyleSheet } from 'react-native'
import React from 'react'
import { CheckIcon, CloseIcon, HStack, Icon, Text, View, VStack } from '@gluestack-ui/themed'
import ColorBox from '../../../../components/ColorBox'

const ToolItem = ({
    color,
    name,
    probability,
    threshold,
}) => {
    var successRecognition = probability > threshold
    var notFound = !probability
    return (
        <HStack p="$0.5" heigh="50px"  width="400px" style={styles.tool_item_container} alignItems='start' alignContent='space-between'>
            <VStack mr='$5' width="250px">
                {/* <ColorBox
                    colorHex={color}
                    colorName={""}
                    isShowText={false}
                /> */}
                <Text size='xs'>{name}</Text>
                {
                    notFound ? <></> :
                        successRecognition ?
                            <View /> : <Text size='xs' color='orange'>Не удается точно определить инструмент</Text>
                }

            </VStack>
            <HStack>
                {
                    notFound ? <></> : <Text size='xs' bold={true}>{(probability * 100).toFixed(2)}%</Text>
                }
                <Icon as={successRecognition ? CheckIcon : CloseIcon} size='xs'
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