import httpx
from pydantic import BaseModel
from typing import List, Optional


class Mentor(BaseModel):
    id: int
    name: dict
    tg_username: str
    tg_chat_id: int
    bday: Optional[str] = None


class MentorsResponse(BaseModel):
    mentors: List[Mentor]


class Postcard(BaseModel):
    id: int
    holidayId: str
    name_ru: str
    body: str


class PostcardsResponse(BaseModel):
    postcards: List[Postcard]    


class AsciiArt(BaseModel):
    ASCIIART: List[str]


def get_mentors_or_congratulations(url, endpoint):
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