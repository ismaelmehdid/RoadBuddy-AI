from fastapi import APIRouter, Request
from typing import Optional
import logging
from typing import Dict

from shared.constants import APIEndpoints
from controllers.driving_exam_chat_contoller import DrivingExamChatController


class ExamChatRoute:

    def __init__(self, driving_exam_chat_controller: DrivingExamChatController, logger: Optional[logging.Logger]) -> None:
        self._driving_exam_chat_controller = driving_exam_chat_controller
        self._logger = logger or logging.getLogger(__name__)
    
    def add_api_routes(self, router: APIRouter) -> None:
        router.add_api_route(APIEndpoints.EXAM_CHAT.value, self.get, methods=['GET'])
    
    async def get(self, request: Request) -> Dict:
        return {"status": "ok"}