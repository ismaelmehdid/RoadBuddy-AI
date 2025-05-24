from pydantic import BaseModel
from typing import Optional, List

class ExamChatQuestionRequestBody(BaseModel):
    question: str
    chat_id: str



class ExamChatQuestionResponseBody(BaseModel):
    response: str
    chat_id: str