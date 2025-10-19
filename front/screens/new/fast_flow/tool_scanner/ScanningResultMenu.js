import { StyleSheet } from 'react-native'
import React from 'react'
import { Box, ButtonText, Card, Heading, ScrollView, Text, VStack } from '@gluestack-ui/themed'
import { Button } from '@gluestack-ui/themed'
import { classColorsMap } from '../Utils'
import ToolItem from './ToolItem'
import { CONFIDENCE_THRESHOLD } from '../../../../App'

const ScanningResultMenu = ({
    toolkitWithRelations,
    onFinishButtonPressed,
    classes,
    probs,
}) => {
    return (
        <Card variant='elevated' height="100%" justifyContent='center' alignItems='center'>
            <Heading size='lg' mb="$3">{`Набор ${toolkitWithRelations != null ? toolkitWithRelations.batch_number : "-"}`}</Heading>
            <VStack space='md'>
                <Button mb='$3' onPress={onFinishButtonPressed}>
                    <ButtonText>Сдать</ButtonText>
                </Button>
            </VStack>
            <ScrollView flex={1}>
                <VStack space='$5'>
                    <Text size='lg' mb='$5'>Инструменты в наборе:</Text>
                    {
                        toolkitWithRelations != null ?
                            toolkitWithRelations.tool_set_type.tool_types.map((toolType) => {
                                const classIndex = classes.indexOf(toolType.tool_class)
                                const toolProb = probs[classIndex]
                                const classColor = classColorsMap.get(toolType.tool_class)
                                //console.log("CLASS_COLOR", classColor)
                                return (<ToolItem
                                    color={classColor}
                                    name={toolType.name}
                                    probability={toolProb}
                                    threshold={CONFIDENCE_THRESHOLD}
                                />)
                            })
                            : <>Загрузка данных о наборе</>
                    }
                </VStack>
            </ScrollView>
        </Card>
    )
}

export default ScanningResultMenu

const styles = StyleSheet.create({})