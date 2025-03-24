import httpx
from pydantic import BaseModel, ValidationError, Field
from typing import List, Optional, Union


class Name(BaseModel):
    first: str
    second: str


class Mentor(BaseModel):
    id: int
    name: Name
    tg_username: str
    tg_chat_id: int
    birthday: Optional[str] = Field(default=None, alias='bday')


class MentorsResponse(BaseModel):
    mentors: List[Mentor]


class Postcard(BaseModel):
    id: int
    holiday_id: str = Field(alias='holidayId')
    name_ru: str
    body: Union[str, List[str]]


class PostcardsResponse(BaseModel):
    postcards: List[Postcard]


def get_mentors_or_congratulations(url, endpoint):
    try:
        if endpoint == '/mentors':
            response_model = MentorsResponse
        elif endpoint == '/postcards':
            response_model = PostcardsResponse
        else:
            raise ValueError("Неверный тип данных")

        full_url = f"{url}{endpoint}"

        response = httpx.get(full_url)
        response.raise_for_status()
        external_data = response.json()

        response_object = response_model(**external_data)

        return response_object

    except ValidationError as e:
        print(f"Ошибка валидации данных: {e}")
        raise
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        raise