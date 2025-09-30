import BannerSize from "./BannerSize"

export default class BannerType {
    constructor(name, displayName, availableSizes) {
        this.name = name
        this.displayName = displayName
        this.availableSizes = availableSizes
    }
}

export const bannerTypes = [
    new BannerType("SQUARE", "Квадратный баннер", [
        new BannerSize("sqb_top", "Сверху"),
        new BannerSize("sqb_bottom", "Снизу"),
    ]),
    new BannerType("GHOST_BANNER_SMALL", "Промо-баннер маленький", [
        new BannerSize("gb_start", "Слева"),
        new BannerSize("gb_end", "Справа"),
    ]),
    new BannerType("GHOST_BANNER_MEDIUM", "Промо-баннер средний", [
        new BannerSize("gb_start", "Слева"),
        new BannerSize("gb_end", "Справа"),
    ]),
    new BannerType("NBO_BANNER", "Баннер NBO", [
        new BannerSize("nbob_top_start", "Сверху слева"),
        new BannerSize("nbob_top_end", "Сверху справа"),
        new BannerSize("nbob_bottom_start", "Снизу слева"),
        new BannerSize("nbob_bottom_end", "Снизу справа"),
    ]),
    new BannerType("RECTANGLE_MB", "Прямоугольный баннер МБ", [
        new BannerSize("ptb_bottom", "Снизу"),
        new BannerSize("ptb_top", "Сверху"),
    ]),
    new BannerType("PART_TRANSPARENT_MB", "Частично-прозрачный баннер МБ", [
        new BannerSize("ptb_bottom", "Снизу"),
        new BannerSize("ptb_top", "Сверху"),
    ])
]