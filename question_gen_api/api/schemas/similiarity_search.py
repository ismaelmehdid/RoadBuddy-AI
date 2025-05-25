from pydantic import BaseModel
from typing import Optional, List


class SimilaritySearchRequestBody(BaseModel):
    query: str


class AnswerChoice(BaseModel):
    id: str
    text: str


class SimilaritySearchResponseBody(BaseModel):
    image_url: str
    question_text: str
    correct_answer_id: str
    choices: List[AnswerChoice]
    explanation: str
    chat_id: str