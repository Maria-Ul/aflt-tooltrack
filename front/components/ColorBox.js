import { Text } from '@gluestack-ui/themed';
import React from 'react';
import {View, StyleSheet} from 'react-native';

const ColorBox = ({colorHex, colorName, isShowText}) => {
  const boxColor = {
    backgroundColor: colorHex,
  };
  const boxText = {
    width: "32px",
    height: "32px",
    color: parseInt(colorHex.replace('#', ''), 16) > 0xffffff / 1.1 ? '#333333' : 'white',
  };
  let text = ""
  if (isShowText){ text = colorName +":"+ colorHex} else  text = ""
  return (
    <View style={[styles.box, boxColor]}>
      <Text style={boxText}> {text}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  box: {
    width: "32px",
    height: "32px",
    borderColor: '#dddddd',
    borderWidth: 1,
    borderStyle: 'solid',
  },
});

export default ColorBox;