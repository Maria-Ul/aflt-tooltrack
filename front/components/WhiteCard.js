import { StyleSheet, Text, View } from 'react-native'
import React from 'react'

const WhiteCard = ({
    withShadow,
    children,
}) => {
  return (
    <View style={styles.white_card}>
        {children}
    </View>
  )
}

export default WhiteCard

const styles = StyleSheet.create({
    white_card: {
        flex: 1,
        backgroundColor: 'white',
        'clip-path': 'inset(0% 0% 0% 0% round 20px)',
    }
})