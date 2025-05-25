from fastapi import APIRouter, Request
from typing import Optional
import logging
from typing import Dict

from shared.constants import APIEndpoints, ExamAnswerMapping
from controllers.similarity_search_controller import SimilaritySearchController
from controllers.driving_exam_chat_contoller import DrivingExamChatController
from api.schemas.similiarity_search import SimilaritySearchRequestBody, SimilaritySearchResponseBody


class SimilaritySearchRoute:

    def __init__(self,
        similarity_search_controller: SimilaritySearchController,
        driving_exam_controller: DrivingExamChatController, 
        logger: Optional[logging.Logger]) -> None:
        self._similarity_search_controller = similarity_search_controller
        self._driving_exam_controller = driving_exam_controller
        self._logger = logger or logging.getLogger(__name__)
    
    def add_api_routes(self, router: APIRouter) -> None:
        router.add_api_route(APIEndpoints.SIMILARITY_SEARCH.value, self.post, methods=['POST'])
    
    async def post(self, body: SimilaritySearchRequestBody) -> SimilaritySearchResponseBody:
        self._logger.info(f"Received request for similiarity search.")

        response = self._similarity_search_controller.search(
            query=body.query,
            top_k=1,
        )
        image_url = response[0]
        chat_id, results = self._driving_exam_controller.generate_driving_questions_for_image(
            image_url=image_url,
        )
        
        result_body = SimilaritySearchResponseBody(
            image_url=image_url,
            question_text=results["question"],
            correct_answer_id=ExamAnswerMapping.get(int(results["correct_answer"])),
            choices=[{
                "id": ExamAnswerMapping.get(i),
                "text": text
            } for i, text in enumerate(results["answers"], start=1)
            ],
            explanation=results["explanation"],
            chat_id=chat_id
        )
        self._logger.info(f"Generated similarity search results")
        return result_body



