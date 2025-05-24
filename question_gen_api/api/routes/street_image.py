from fastapi import APIRouter, Request
from typing import Optional
import logging
from typing import Dict

from shared.constants import APIEndpoints
from controllers.street_image_controller import StreetImageController
from api.schemas.street_image import StreetImageRequestBody, StreetImageResponseBody


class StreetImageRoute:

    def __init__(self, street_image_controller: StreetImageController, logger: Optional[logging.Logger]) -> None:
        self._street_image_controller = street_image_controller
        self._logger = logger or logging.getLogger(__name__)
    
    def add_api_routes(self, router: APIRouter) -> None:
        router.add_api_route(APIEndpoints.STREET_IMAGE.value, self.post, methods=['POST'])
    
    async def post(self, body: StreetImageRequestBody) -> StreetImageResponseBody:
        self._logger.info(f"Received request for street image.")

        image_url = self._street_image_controller.get_street_image_url(
            city=body.city,
        )

        result_body = StreetImageResponseBody(
            image_url=image_url,
        )
        self._logger.info(f"Generated street image results")
        return result_body