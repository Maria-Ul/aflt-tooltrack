import React from 'react';
import {View, StyleSheet} from 'react-native';

const ColorSquare = ({colorHex}) => {
  const boxColor = {
    backgroundColor: colorHex,
  };
  return <View style={[styles.box, boxColor]} />;
};

const styles = StyleSheet.create({
  box: {
    width: "1.5em",
    height: "1.5em",
    marginRight: 8,
    borderColor: '#dddddd',
    borderWidth: 2,
    borderStyle: 'solid',
  },
});

export default ColorSquare;