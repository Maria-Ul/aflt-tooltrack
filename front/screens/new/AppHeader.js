import { Button, ButtonIcon, ButtonText, HStack, Image, MenuIcon } from "@gluestack-ui/themed"
import AsyncStorage from "@react-native-async-storage/async-storage"
import { useNavigation } from "@react-navigation/native";
import { StyleSheet, Text, View } from 'react-native';

const APP_HEADER_HEIGHT = 80

export const headerStyle = {
  height: APP_HEADER_HEIGHT,
  backgroundColor: "#F4F6FA"
}

export const preloginHeaderLeft = () => (
    <Image ml='$5' mr='$10'
        style={styles.headerLogoImage}
        source={require("../../assets/logo_aeroflot.png")} />
)

export const headerLeft = () => (
    <HStack alignItems='center'>
        {/* <Button variant='outline' ml='$5' mr='$2'>
            <ButtonIcon as={MenuIcon} />
        </Button> */}
        <Image ml='$5' mr='$10'
            style={styles.headerLogoImage}
            source={require("../../assets/logo_aeroflot.png")} />
    </HStack>
)

export const headerRight = () => {
    const navigation = useNavigation()
    const onExit = () => {
        AsyncStorage.setItem(SESSION_TOKEN, "")
        navigation.navigate("Auth")
    }
    const onUserGuide = () => {
        navigation.navigate("UserGuide")
    }
    return (
        <HStack space='xs'>
            {/* <Avatar>
          <AvatarFallbackText></AvatarFallbackText>
        </Avatar>
        <Heading mr='$5'></Heading> */}
            <Button mr="$5" variant="outline" onPress={onUserGuide}>
                <ButtonText>Инструкция</ButtonText>
            </Button>
            <Button mr='$5' variant="outline" onPress={onExit}>
                <ButtonText>Выйти</ButtonText>
            </Button>
        </HStack>
    )
}

export const preloginHeaderRight = () => {
    const navigation = useNavigation()
    const onUserGuide = () => {
        navigation.navigate("UserGuide")
    }
    return (
        <Button mr="$5" variant="outline" onPress={onUserGuide}>
            <ButtonText>Инструкция</ButtonText>
        </Button>
    )
}

export const guideHeaderRight = () => {
    const navigation = useNavigation()
    const onBack = () => {
        navigation.goBack()
    }
    return (
        <Button mr="$5" variant="outline" onPress={onBack}>
            <ButtonText>Назад</ButtonText>
        </Button>
    )
}

const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: '#fff',
      alignItems: 'center',
      justifyContent: 'center',
    },
    headerLogoImage: {
      resizeMode: "contain",
      width: 250,
      height: APP_HEADER_HEIGHT,
    }
  });