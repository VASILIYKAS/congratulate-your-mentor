import httpx
from pydantic import BaseModel, ValidationError
from typing import List


class Mentor(BaseModel):
    last_name: str
    first_name: str
    tg_id: int


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

    try:
        response = httpx.get(url)
        response.status_code
        response.raise_for_status()
        external_data = response.json()

        response_object = response_model(**external_data)

        return response_object.model_dump_json()

    except httpx.ConnectError:
        print('Ошибка соединения: не удалось подключиться к серверу.')
    except ValidationError as e:
        print('Ошибка формата ответа: неправильный формат данных в json файле',
              e.errors())
    except httpx.HTTPError as exc:
        print('Произошла ошибка при выполнении запроса.')
        print(f'Код ошибки: {response.status_code} URL: {exc.request.url!r}.')