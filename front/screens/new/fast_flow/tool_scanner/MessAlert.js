import React from 'react'

const MessAlert = ({ style }) => {
    return (
        <HStack style={style} p="$3" space='md' bgColor='#f79494ff'
            borderWidth="2px" borderColor='#ff0000ff' alignItems='center'>
            <Icon as={TriangleAlertIcon} size='xl' />
            <Text size="lg" bold="true">{`Кажется, инструменты перекрывают друга друга.\n
            Попробуйте разложить их более равномерно`}</Text>
        </HStack>
    )
}

export default MessAlert