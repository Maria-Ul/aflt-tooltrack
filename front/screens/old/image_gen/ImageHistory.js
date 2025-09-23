import { Text } from "@rneui/themed"
import { FlatList, StyleSheet, View } from "react-native"
import ImageResponseItem from "./ImageResponseItem";
import { ButtonText, HStack, ScrollView, VStack } from "@gluestack-ui/themed";
import { useEffect, useState } from "react";
import { historyRequest } from "../../api/history";
import { Button } from "react-native-web";

const ImageHistory = ({ imageHistory, refreshHistory }) => {
    // const renderHistoryItems = () => {
    //     return imageHistory.map((historyItem) => {
    //         return (

    //         )
    //     })
    // }
    const [refreshTrigger, setRefreshTrigger] = useState(false)
    const [previousImageHistory, setPreviousImageHistory] = useState(imageHistory)
    console.log(previousImageHistory)
    
    useEffect( () => {
        if (previousImageHistory.find((item, index) => {
            var n = imageHistory[index]
            return `${n.id}_${n.status}` != `${item.id}_${item.status}`
        }) != undefined || previousImageHistory.length == 0) {
            console.log("changed" + imageHistory)
            setPreviousImageHistory(imageHistory)
        }
    }
    ,[imageHistory])

    //console.log(imageHistory)
    return (
        <ScrollView w="100%" h="100%">
            <VStack p="$10" space="md">
                {
                    //renderHistoryItems()
                }
                <FlatList
                    data={previousImageHistory}
                    renderItem={
                        ({item, index, separators}) => {
                            const historyItem = item
                            var pPrompt = Object.hasOwn(historyItem.options, 'positive_prompt') ?
                                historyItem.options.positive_prompt : ""
                            return <ImageResponseItem
                                key={historyItem.id}
                                status={historyItem.status}
                                imageId={historyItem.id}
                                productType={""}
                                originalPromt={pPrompt}
                                imageName={historyItem.object_name}
                                imageWidth={historyItem.options.width}
                                imageHeight={historyItem.options.height}
                                onRefresh={refreshHistory}
                            />
                            }
                    }
                    keyExtractor={item => item.id}
                    //extraData={imageHistory}
                />
            </VStack>
        </ScrollView>
    )
}

export default ImageHistory;

const styles = StyleSheet.create({
    responseHistory: {

    },
    clearHistoryButton: {
        position: "absolute",
        left: 0,
        top: 0,
        elevation: 10,
        width: 100,
        height: 64,
    },
    refreshButton: {
        position: "absolute",
        left: 0,
        top: 50,
        elevation: 10,
        width: 100,
        height: 64,
    }
})