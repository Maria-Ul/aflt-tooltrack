import { StyleSheet, Text, View } from 'react-native'
import React from 'react'
import { Card, Center, Icon } from '@gluestack-ui/themed'
import { VideoOffIcon } from 'lucide-react-native'

const AuthStagePreview = () => {
  return (
    <Card variant='filled' backgroundColor='grey' height="100%">
        <Center height="100%">
            <Icon as={VideoOffIcon} size="xl" color='white'/>
        </Center>
    </Card>
  )
}

export default AuthStagePreview

const styles = StyleSheet.create({})