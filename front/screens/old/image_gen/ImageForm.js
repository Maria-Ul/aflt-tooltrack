import { StyleSheet, TouchableOpacity, View } from "react-native"
import { useEffect, useState } from "react"
import { HStack, VStack, Text, Icon, ScrollView, Textarea, TextareaInput, Center, Switch } from '@gluestack-ui/themed';
import { Input, InputField } from '@gluestack-ui/themed';
import { Divider } from "@gluestack-ui/themed"
import {
    Select,
    SelectTrigger,
    SelectIcon,
    SelectInput,
    SelectPortal,
    SelectBackdrop,
    SelectDragIndicatorWrapper,
    SelectDragIndicator,
    SelectContent,
    SelectItem,
} from '@gluestack-ui/themed';
import {
    Accordion,
    AccordionHeader,
    AccordionItem,
    AccordionTrigger,
    AccordionContent,
    AccordionIcon,
    AccordionTitleText,
    ChevronDownIcon,
    ChevronUpIcon,
} from '@gluestack-ui/themed';
import {
    Button,
    ButtonText,
    ButtonIcon,
    ButtonSpinner,
    ButtonGroup,
} from "@gluestack-ui/themed"
import { EXTRA_COLOR } from "../../ColorConst";
import ColorBox from "../../components/ColorBox";
import ColorSquare from "../../components/ColorSquare";
import { bannerTypes } from "../../model/banner/BannerType";
import { bannerColors } from "../../model/banner/BannerColors";
import { TASK_TYPE_IMAGE, generateRequest } from "../../api/generate";

const ImageForm = ({
    onClearImageHistory,
    onRefreshImageHistory,
}) => {
    const [imageWidth, setImageWidth] = useState(512)
    const [imageHeight, setImageHeight] = useState(512)
    const [imagesCount, setImagesCount] = useState(1)
    const [productType, setProductType] = useState("")
    const [customerCategory, setCustomerCategory] = useState("")

    const [positivePrompt, setPositivePrompt] = useState('')
    const [negativePrompt, setNegativePrompt] = useState('')

    const onGenerateImage = () => {
        generateRequest({
            taskType: TASK_TYPE_IMAGE,
            taskData: {
                count: imagesCount,
                width: imageWidth,
                height: imageHeight,
                product_type: productType,
                positive_prompt: positivePrompt,
                negative_prompt: negativePrompt,
                category: customerCategory,
                offer: productType,
            },
            onSuccess: () => {
                onRefreshImageHistory()
            }
        })
    }

    const onClearInput = () => {
        setImageWidth(512)
        setImageHeight(512)
        setImagesCount(1)
        setProductType("")
        setPositivePrompt("")
        setNegativePrompt("")
    }

    const onImageHeghtChanged = (text) => {
        var i = parseInt(text)
        setImageHeight(i)
    }

    const onImageWidthChanged = (text) => {
        var i = parseInt(text)
        setImageWidth(i)
    }

    return (
        <ScrollView>
            <VStack p="$3" space="md">
                <Text size="xl" bold="true">Параметры изображений</Text>
                <Text size="md">Высота</Text>
                <Input>
                    <InputField value={imageHeight} onChangeText={onImageHeghtChanged} placeholder="Высота" />
                </Input>
                <Text size="md">Ширина</Text>
                <Input>
                    <InputField value={imageWidth} onChangeText={onImageWidthChanged} placeholder="Ширина" />
                </Input>
                <Text size="md">Количество изображений</Text>
                <Input>
                    <InputField value={imagesCount} onChangeText={setImagesCount} valueplaceholder="Количество изображений" />
                </Input>
                <Text size="md">Тип рекламируемого продукта</Text>
                <Select
                    selectedValue={productType}
                    onValueChange={setProductType}
                >
                    <SelectTrigger variant="outline" size="md">
                        <SelectInput placeholder="Тип продукта" />
                        <SelectIcon mr="$3">
                            <Icon as={ChevronDownIcon} />
                        </SelectIcon>
                    </SelectTrigger>
                    <SelectPortal>
                        <SelectBackdrop />
                        <SelectContent>
                            <SelectDragIndicatorWrapper>
                                <SelectDragIndicator />
                            </SelectDragIndicatorWrapper>
                            <SelectItem label="Ипотека" value="home mortgage" />
                            <SelectItem label="Кредитная карта" value="credit card" />
                            <SelectItem label="Автокредит" value="car loan" />
                            <SelectItem label="Премиум" value="premium account" />
                        </SelectContent>
                    </SelectPortal>
                </Select>
                <Text size="md">Категория клиентских трат</Text>
                <Select
                    selectedValue={customerCategory}
                    onValueChange={setCustomerCategory}
                >
                    <SelectTrigger variant="outline" size="md">
                        <SelectInput placeholder="Категория" />
                        <SelectIcon mr="$3">
                            <Icon as={ChevronDownIcon} />
                        </SelectIcon>
                    </SelectTrigger>
                    <SelectPortal>
                        <SelectBackdrop />
                        <SelectContent>
                            <SelectDragIndicatorWrapper>
                                <SelectDragIndicator />
                            </SelectDragIndicatorWrapper>
                            <SelectItem label="Путешествия" value="travel" />
                            <SelectItem label="Красота и здоровье" value="health and beauty" />
                            <SelectItem label="Связь и Интернет" value="mobile communications and internet" />
                            <SelectItem label="Заправки" value="gas stations" />
                        </SelectContent>
                    </SelectPortal>
                </Select>

                {/* <Text size="xl" bold="true">Данные о клиенте</Text>
                <Button onPress={"getImage"} size="lg">
                    <ButtonText>Загрузить</ButtonText>
                </Button> */}

                <Accordion
                    size="lg"
                    variant="unfilled"
                    type="single"
                    isCollapsible={true}
                    isDisabled={false}
                >
                    <AccordionItem value="a" backgroundColor={EXTRA_COLOR}>
                        <AccordionHeader m="$0">
                            <AccordionTrigger m="0$">
                                {({ isExpanded }) => {
                                    return (
                                        <>
                                            <AccordionTitleText>
                                                <Text size="lg" bold="true">Дополнительные параметры генерации</Text>
                                            </AccordionTitleText>
                                            {isExpanded ? (
                                                <AccordionIcon as={ChevronUpIcon} ml="$3" />
                                            ) : (
                                                <AccordionIcon as={ChevronDownIcon} ml="$3" />
                                            )}
                                        </>
                                    )
                                }}
                            </AccordionTrigger>
                        </AccordionHeader>
                        <AccordionContent pt="2$" mt="0$">
                            <VStack space="md" m="0$">
                                <Textarea m="0$">
                                    <TextareaInput value={positivePrompt} onChangeText={setPositivePrompt} placeholder="Промт" />
                                </Textarea>
                                <Textarea>
                                    <TextareaInput value={negativePrompt} onChangeText={setNegativePrompt} placeholder="Негативный промт" />
                                </Textarea>
                                {/* <Text size="md">Пресеты</Text>
                                <HStack space="3xl">
                                    <Badge size="md" variant="outline" borderRadius="$full" action="info">
                                        <BadgeText>Опция 1</BadgeText>
                            
                                    </Badge>
                                    <Badge size="md" variant="outline" borderRadius="$full" action="info">
                                        <BadgeText>Опция 1</BadgeText>
                                    </Badge>
                                    <Badge size="md" variant="outline" borderRadius="$full" action="info">
                                        <BadgeText>Удалить фон таким образом, чтобы ......</BadgeText>
                                    </Badge>
                                </HStack> */}
                            </VStack>
                        </AccordionContent>
                    </AccordionItem>
                </Accordion>
                <Divider my="$1" />
                <HStack space="md">
                    <Button
                        w="45%"
                        onPress={onGenerateImage}
                        size="lg"
                        isDisabled={
                            !(
                                (imageHeight > 64 && imageHeight < 1024) &&
                                (imageWidth > 64 && imageWidth < 1024) &&
                                productType != "" && customerCategory != ""
                            )
                        }
                    >
                        <ButtonText>Сгенерировать</ButtonText>
                    </Button>
                    <Button w="45%" onPress={onClearInput} size="lg" action="negative">
                        <ButtonText>Очистить ввод</ButtonText>
                    </Button>
                </HStack>
                <Button w="100%" onPress={onRefreshImageHistory} size="lg">
                    <ButtonText>Обновить</ButtonText>
                </Button>
                <Button w="100%" onPress={onClearImageHistory} size="lg">
                    <ButtonText>Очистить историю</ButtonText>
                </Button>
            </VStack>
        </ScrollView>
    )
}

export default ImageForm;

const styles = StyleSheet.create(
    {
        noTopMargin: {
            margin: "0",
        }
    }
)