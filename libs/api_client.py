import httpx
from pydantic import BaseModel
from typing import List


class Mentor(BaseModel):
    last_name: str
    first_name: str
    tg_id: int
    user_name: str


class MentorsResponse(BaseModel):
    mentors: List[Mentor]


class Congratulations(BaseModel):
    congratulations: List[str]


class AsciiArt(BaseModel):
    ASCIIART: List[str]


def get_mentors_or_congratulations(url, endpoint):
    if endpoint == 'mentors':
        response_model = MentorsResponse
    elif endpoint == 'congratulations':
        response_model = Congratulations
    elif endpoint == 'asciiart':
        response_model = AsciiArt
    else:
        raise ValueError("Неверный тип данных")

    response = httpx.get(url)
    response.status_code
    response.raise_for_status()
    external_data = response.json()

    response_object = response_model(**external_data)

    return response_object