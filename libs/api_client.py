import httpx
from validators import MentorsResponse, Congratulations, AsciiArt
from pydantic import ValidationError


def get_mentors_or_congratulations(url, endpoint):
    try:
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

    except ValidationError as e:
        raise e
    except httpx.HTTPError as e:
        raise e
    except Exception as e:
        raise e