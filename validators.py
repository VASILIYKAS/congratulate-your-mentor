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