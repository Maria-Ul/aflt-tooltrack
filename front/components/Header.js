import { Text } from "@rneui/base"
import { StyleSheet, View } from "react-native"
import { Col, Row, Grid } from "react-native-easy-grid"

const Header = ({}) => {
    return(
        <View style={styles.header}>
            <Text>Hello!</Text>
        </View>
    )
}

const styles = StyleSheet.create({
    header: {
        backgroundColor: "black",
    }
})

export default Header;