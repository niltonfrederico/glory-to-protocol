from pydantic import BaseModel


class StampStrings(BaseModel):
    approved: str = "ОДОБРЕНО"
    rejected: str = "ОТКАЗАНО"
    pending: str = "В ОЧЕРЕДИ"


class PaletteStrings(BaseModel):
    title: str = "ДИРЕКТИВЫ"
    empty: str = "Нет директив."
    placeholder: str = "Найти директиву…"


class FormStrings(BaseModel):
    submit: str = "ОТПРАВИТЬ"
    cancel: str = "ОТМЕНИТЬ"
    required: str = "Обязательное поле"


class HeaderStrings(BaseModel):
    motto: str = "Слава ПРОТОКОЛУ"


class ViewportStrings(BaseModel):
    too_small_title: str = "ОКНО СЛИШКОМ МАЛО"
    too_small_body: str = "Требуется {min_w}×{min_h}. Текущее: {cur_w}×{cur_h}."
    fullscreen_hint: str = "ПОЛНЫЙ ЭКРАН РЕКОМЕНДУЕТСЯ"


class Strings(BaseModel):
    stamps: StampStrings = StampStrings()
    palette: PaletteStrings = PaletteStrings()
    forms: FormStrings = FormStrings()
    header: HeaderStrings = HeaderStrings()
    viewport: ViewportStrings = ViewportStrings()
