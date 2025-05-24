from fastapi import APIRouter, Request
from typing import Optional
import logging
from typing import Dict

from shared.constants import APIEndpoints
from controllers.driving_exam_chat_contoller import DrivingExamChatController
from api.schemas.exam_chat import ExamChatRequestBody, ExamChatResponseBody


class ExamChatRoute:

    def __init__(self, driving_exam_chat_controller: DrivingExamChatController, logger: Optional[logging.Logger]) -> None:
        self._driving_exam_chat_controller = driving_exam_chat_controller
        self._logger = logger or logging.getLogger(__name__)
    
    def add_api_routes(self, router: APIRouter) -> None:
        router.add_api_route(APIEndpoints.EXAM_CHAT.value, self.post, methods=['POST'])
    
    async def post(self, body: ExamChatRequestBody) -> ExamChatResponseBody:
        self._logger.info(f"Received request for exam chat.")

        chat_id, results = self._driving_exam_chat_controller.generate_driving_questions_for_image(
            image_url=body.image_url,
            city=body.city
        )

        result_body = ExamChatResponseBody(
            image_url=body.image_url,
            correct_answer_id=int(results["correct_answer"]),
            question_text=results["question"],
            choices=[{
                "id": i,
                "text": text
            } for i, text in enumerate(results["answers"], start=1)
            ],
            explanation=results["explanation"],
            chat_id=chat_id
        )
        self._logger.info(f"Generated exam chat results")
        return result_body