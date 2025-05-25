import os
import logging
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from mistralai import Mistral
from mangum import Mangum
from dotenv import load_dotenv, find_dotenv

from clients.s3_client import AWSS3Client
from clients.role_assumer_client import AWSRoleAssumer
from controllers.driving_exam_chat_contoller import DrivingExamChatController
from controllers.street_image_controller import StreetImageController
from controllers.similarity_search_controller import SimilaritySearchController
from api.routes.exam_chat import ExamChatRoute
from api.routes.exam_chat_question import ExamChatQuestionRoute
from api.routes.street_image import StreetImageRoute
from api.routes.similarity_search import SimilaritySearchRoute
from api.routes.liveness import LivenessRoute
from shared.constants import (
    APIEndpoints,
)

load_dotenv(find_dotenv(), override=True)
    

def create_app(
    logger: logging.Logger,
    s3_client: AWSS3Client,
    mistral_client: Mistral,
    mapillary_token: str,
    index_url: str,
    index_token: str,
    env: str='prod'
    ) -> FastAPI:
    
    app = FastAPI(
        docs_url=APIEndpoints.DOCS.value,
        redoc_url=APIEndpoints.REDOC.value,
        openapi_url=APIEndpoints.OPENAPI_URL.value
    )
    
    #cors settings
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    
    router = APIRouter()
    
    
    driving_exam_chat_controller = DrivingExamChatController(
        mistral_client=mistral_client,
        s3_client=s3_client,
        logger=logger
    )

    #street_image_controller = StreetImageController(api_token=mapillary_token)

    similarity_search_controller = SimilaritySearchController(
        index_url=index_url,
        api_key=index_token,
        mistral_client=mistral_client,
        logger=logger,
    )

    exam_chat_route = ExamChatRoute(driving_exam_chat_controller, logger)
    logger.info("Adding exam chat routes")
    exam_chat_route.add_api_routes(router)
    logger.info("Added exam chat routes")

    exam_chat_route = ExamChatQuestionRoute(driving_exam_chat_controller, logger)
    logger.info("Adding exam question chat routes")
    exam_chat_route.add_api_routes(router)
    logger.info("Added exam question chat routes")

    exam_chat_route = StreetImageRoute(logger)
    logger.info("Adding street image routes")
    exam_chat_route.add_api_routes(router)
    logger.info("Added street image routes")

    exam_chat_route = SimilaritySearchRoute(similarity_search_controller, driving_exam_chat_controller, logger)
    logger.info("Adding similariy search routes")
    exam_chat_route.add_api_routes(router)
    logger.info("Added similariy search routes")
    

    liveness_route = LivenessRoute()
    logger.info("Adding liveness routes")
    liveness_route.add_api_routes(router)
    logger.info("Added liveness routes")
    
    app.include_router(router)
    return app



FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
ENV = os.getenv("ENV", "prod")

mapillary_token = os.getenv("MAPILLARY_TOKEN")
mistral_api_key = os.getenv("MISTRAL_API_KEY")
index_url = os.getenv("VECTOR_DB_ENDPOINT", None)
index_token = os.getenv("VECTOR_DB_API_KEY", None)
mistral_client = Mistral(api_key=mistral_api_key)

role_arn = os.getenv("AWS_ROLE_ARN", None)
if role_arn :
    aws_role_assumer = AWSRoleAssumer(role_arn, rotation_minutes=30)
else:
    aws_role_assumer = None

s3_client = AWSS3Client(aws_role_assumer)


logger = logging.getLogger('driving_exam_chat')
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter(FORMAT))
logger.addHandler(handler)
    
try:
    app = create_app(
        logger=logger,
        s3_client=s3_client,
        mistral_client=mistral_client,
        mapillary_token=mapillary_token,
        index_url=index_url,
        index_token=index_token,
        env=ENV
        )
except Exception as e:
    logger.error("An error occurred during startup")
    logger.error(e)
    raise e

logger.info("Starting FastAPI application")

handler = Mangum(app)
    
    
    