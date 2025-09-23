import { StyleSheet, Text, View } from 'react-native'
import React, { useRef } from 'react'
import { CameraView } from 'expo-camera'

const ToolsScanerScreen = ({ navigation }) => {
    const ref = useRef(null)
    return (
        <View>
            <Text>ToolsScanerScreen</Text>
            <CameraView ref={ref}
                style={styles.camera} mode='video'
            />
        </View>
    )
}

export default ToolsScanerScreen

const styles = StyleSheet.create({
    camera: {
        width: "300px",
        height: "300px",
    }
})