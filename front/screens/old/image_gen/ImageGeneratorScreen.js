import { View, Image, StyleSheet } from "react-native"

import { useEffect, useState } from "react";
import axios from 'axios';
import { Col, Grid, Row } from "react-native-easy-grid";
import ImageHistory from "./ImageHistory";
import ImageForm from "./ImageForm";
import Header from "../../components/Header";
import { historyRequest } from "../../api/history";
import { clearHistoryRequest } from "../../api/clearHistory";

const ImageGeneratorScreen = ({ navigation }) => {
    const [imageHistory, setImageHistory] = useState([])

    useEffect(() => {
        // Использовать web-socket в будущем!!!
        var timerId = setInterval(refreshHistory, 5000)
        navigation.addListener('beforeRemove', (e) => {
            clearInterval(timerId)
        })
    }, [navigation])

    const refreshHistory = () => {
        historyRequest({
            onSuccess: (data) => { setImageHistory(data) }
        })
    }
    const clearHistory = () => {
        clearHistoryRequest(
            {
                onSuccess: () => { setImageHistory() }
            }
        )
    }
    useEffect(() => { refreshHistory() }, [])
    return (
        <Grid>
            <Row>
                <Col size={1} style={{ backgroundColor: "white" }}>
                    <ImageForm
                        onClearImageHistory={clearHistory}
                        onRefreshImageHistory={refreshHistory}
                    />
                </Col>
                <Col size={2}>
                    <ImageHistory
                        imageHistory={imageHistory}
                        refreshHistory={refreshHistory}
                    />
                </Col>
            </Row>
        </Grid>
    );
}

export default ImageGeneratorScreen;

const styles = StyleSheet.create({
    logo: {
        width: 400,
        height: 400,
    },
});