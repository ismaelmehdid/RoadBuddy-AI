from fastapi import APIRouter, Request
from typing import Optional
import logging
from typing import Dict

from shared.constants import APIEndpoints
from controllers.driving_exam_chat_contoller import DrivingExamChatController
from api.schemas.exam_chat_question import ExamChatQuestionRequestBody, ExamChatQuestionResponseBody


class ExamChatQuestionRoute:

    def __init__(self, driving_exam_chat_controller: DrivingExamChatController, logger: Optional[logging.Logger]) -> None:
        self._driving_exam_chat_controller = driving_exam_chat_controller
        self._logger = logger or logging.getLogger(__name__)
    
    def add_api_routes(self, router: APIRouter) -> None:
        router.add_api_route(APIEndpoints.EXAM_CHAT_QUESTION.value, self.post, methods=['POST'])
    
    async def post(self, body: ExamChatQuestionRequestBody) -> ExamChatQuestionResponseBody:
        self._logger.info(f"Received request for exam chat.")

        response = self._driving_exam_chat_controller.ask_followup_question(
            question=body.question,
            chat_id=body.chat_id,
        )
        
        print(f"Response: {response}")
        result_body = ExamChatQuestionResponseBody(
            response=response,
            chat_id=body.chat_id
        )
        self._logger.info(f"Generated exam chat results")
        return result_body