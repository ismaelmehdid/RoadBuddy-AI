from dotenv import load_dotenv, find_dotenv
from mistralai import Mistral
from typing import Optional
import logging
import os
load_dotenv(find_dotenv(), override=True)

from clients.s3_client import AWSS3Client
from clients.role_assumer_client import AWSRoleAssumer

from controllers.street_image_controller import StreetImageController
from controllers.driving_exam_chat_contoller import DrivingExamChatController
from controllers.similarity_search_controller import SimilaritySearchController


def fill_index_with_questions(
    street_image_controller: StreetImageController,
    driving_exam_chat_controller: DrivingExamChatController,
    similarity_search_controller: SimilaritySearchController,
    count: int = 5000,
    city: str = "Paris",
    logger: Optional[logging.Logger] = None
    ):
    logger = logger or logging.getLogger(__name__)
    logger.info("Starting to fill index with questions...")
    for i in range(count):
        try:
            image_url = street_image_controller.get_street_image_url(city=city)
            chat_id, results = driving_exam_chat_controller.generate_driving_questions_for_image(
                image_url=image_url,
                city=city
            )
            similarity_search_controller.add_question(
                question_id=chat_id,
                question=results["question"],
                image_url=image_url
            )
            logger.info(f"Added question {i+1}/{count} to index.")
        except Exception as e:
            logger.error(f"Error processing image {i+1}: {e}")

if __name__ == "__main__":

    logger = logging.getLogger("init_street_image_questions_index")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    mapillary_token = os.getenv("MAPILLARY_TOKEN")
    mistral_api_key = os.getenv("MISTRAL_API_KEY")
    index_url = os.getenv("VECTOR_DB_ENDPOINT", None)
    index_token = os.getenv("VECTOR_DB_API_KEY", None)
    
    role_arn = os.getenv("AWS_ROLE_ARN", None)
    if role_arn :
        aws_role_assumer = AWSRoleAssumer(role_arn, rotation_minutes=30)
    else:
        aws_role_assumer = None

    s3_client = AWSS3Client(aws_role_assumer)

    mistral_client = Mistral(api_key=mistral_api_key)
    street_image_controller = StreetImageController(api_token=mapillary_token)
    driving_exam_chat_controller = DrivingExamChatController(
        mistral_client=mistral_client,
        s3_client=s3_client,
        logger=logger,
    )
    similarity_search_controller = SimilaritySearchController(
        index_url=index_url,
        api_key=index_token,
        mistral_client=mistral_client,
        logger=logger,
    )

    fill_index_with_questions(
        street_image_controller=street_image_controller,
        driving_exam_chat_controller=driving_exam_chat_controller,
        similarity_search_controller=similarity_search_controller,
        count=5000,  # Adjust the count as needed
        city="Paris",  # Adjust the city as needed
        logger=logger
    )
    logger.info("Index filling completed.")



