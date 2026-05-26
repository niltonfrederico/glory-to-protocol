from pydantic import BaseModel
from pydantic import Field


class StampStrings(BaseModel):
    approved: str = Field("ОДОБРЕНО")
    rejected: str = Field("ОТКАЗАНО")
    pending: str = Field("В ОЧЕРЕДИ")


class PaletteStrings(BaseModel):
    title: str = Field("ДИРЕКТИВЫ")
    empty: str = Field("Нет директив.")
    placeholder: str = Field("Найти директиву…")


class FormStrings(BaseModel):
    submit: str = Field("ОТПРАВИТЬ")
    cancel: str = Field("ОТМЕНИТЬ")
    required: str = Field("Обязательное поле")


class HeaderStrings(BaseModel):
    motto: str = Field("Слава ПРОТОКОЛУ")


class ViewportStrings(BaseModel):
    too_small_title: str = Field("ОКНО СЛИШКОМ МАЛО")
    too_small_body: str = Field("Требуется {min_w}×{min_h}. Текущее: {cur_w}×{cur_h}.")
    fullscreen_hint: str = Field("ПОЛНЫЙ ЭКРАН РЕКОМЕНДУЕТСЯ")


class Strings(BaseModel):
    stamps: StampStrings = StampStrings()
    palette: PaletteStrings = PaletteStrings()
    forms: FormStrings = FormStrings()
    header: HeaderStrings = HeaderStrings()
    viewport: ViewportStrings = ViewportStrings()
