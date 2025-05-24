from enum import Enum
MISTRAL_BASE_URL = "https://api.mistral.ai/v1"
MISTRAL_IMAGE_TEXT_MODEL = "pixtral-12b-2409"

S3_BUCKET_NAME = "hackathon-ai-tech"

class APIEndpoints(Enum):
    DOCS = "/api/v1/docs"
    REDOC = "/api/v1/redoc"
    OPENAPI_URL = "/api/v1/openapi.json"
    LIVENESS = "/api/v1/healthy"
    EXAM_CHAT = "/api/v1/exam-chat"
    EXAM_CHAT_QUESTION = "/api/v1/exam-chat-question"


