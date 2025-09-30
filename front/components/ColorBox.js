import { Text } from '@gluestack-ui/themed';
import React from 'react';
import {View, StyleSheet} from 'react-native';

const ColorBox = ({colorHex, colorName, isShowText}) => {
  const boxColor = {
    backgroundColor: colorHex,
  };
  const boxText = {
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
    marginBottom: 10,
    paddingVertical: 10,
    paddingHorizontal: 10,
    alignItems: 'center',
    borderColor: '#dddddd',
    borderWidth: 1,
    borderStyle: 'solid',
  },
});

export default ColorBox;