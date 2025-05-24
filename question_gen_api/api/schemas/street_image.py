from pydantic import BaseModel
from typing import Optional

class StreetImageRequestBody(BaseModel):
    city: str = "Paris"

class StreetImageResponseBody(BaseModel):
    image_url: Optional[str] = None