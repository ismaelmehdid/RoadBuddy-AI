from fastapi import APIRouter, Request
from typing import Dict

from shared.constants import APIEndpoints


class LivenessRoute:

    def __init__(self) -> None:
        pass
    
    def add_api_routes(self, router: APIRouter) -> None:
        router.add_api_route(APIEndpoints.LIVENESS.value, self.get, methods=['GET'])
    
    async def get(self, request: Request) -> Dict:
        return {"status": "ok"}