import logging
import uuid
import json
from datetime import datetime
from typing import Optional, Dict
from mistralai import Mistral
from clients.s3_client import AWSS3Client
from shared.prompts import DRIVING_EXAM_CHAT_SYSTEM_PROMPT, DRIVING_EXAM_CHAT_SYSTEM_PROMPT_FOLLOW_UP, DRIVING_EXAM_CHAT_USER_PROMPT
from shared.constants import MISTRAL_IMAGE_TEXT_MODEL

class DrivingExamChatController:

    def __init__(self, mistral_client: Mistral, s3_client: AWSS3Client, logger: Optional[logging.Logger] = None) -> None:
        self._mistral_client = mistral_client
        self._s3_client = s3_client
        self._logger = logger or logging.getLogger(__name__)
        self._active_chats = {}

    

    def generate_driving_questions_for_image(self, image_url: str, chat_id: Optional[str] = None, city: Optional[str] = "Paris") -> Dict:
        if not chat_id:
            chat_id = self._generate_chat_id()
        else:
            self._download_chat_history(chat_id)
        system_messages = DRIVING_EXAM_CHAT_SYSTEM_PROMPT % (city)
        chat = self._active_chats[chat_id]
        chat["messages"].append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": DRIVING_EXAM_CHAT_USER_PROMPT,
                },
                {
                    "type": "image_url",
                    "image_url": image_url,
                },
            ]
        })
        response = self._mistral_client.chat.complete(
            model="pixtral-12b-2409",
            messages=[
                {
                    "role": "system",
                    "content": system_messages,
                },
                *chat["messages"],
            ],
        )
        self._active_chats[chat_id]["messages"].append({
            "role": "assistant",
            "content": response.model_dump()["choices"][0]["message"]["content"],
        })
        self._save_chat_history(chat_id)
        self._logger.info(f"Generated driving questions for image {image_url} in chat {chat_id}")

        try:
            question_parsed = json.loads('{' + response.model_dump()["choices"][0]["message"]["content"].split('{')[1].split('}')[0] + '}')
            result = {
                "question": question_parsed.get("question", ""),
                "answers": question_parsed.get("answers", []),
                "explanation": question_parsed.get("explanation", ""),
                "correct_answer": question_parsed.get("correct_answer", ""),

            }
        except json.JSONDecodeError as e:
            result = {
                "question": "",
                "answers": [],
                "explanation": "",
                "correct_answer": "",
            }
        return chat_id, result


    def ask_followup_question(self, question: str, chat_id: Optional[str] = None) -> str:
        if not chat_id:
            chat_id = self._generate_chat_id()
        else:
            self._download_chat_history(chat_id)
        chat = self._active_chats[chat_id]
        chat["messages"].append({
            "role": "user",
            "content": question
        })
        system_messages = DRIVING_EXAM_CHAT_SYSTEM_PROMPT_FOLLOW_UP
        response = self._mistral_client.chat.complete(
            model="pixtral-12b-2409",
            messages=[
                {
                    "role": "system",
                    "content": system_messages,
                },
                *chat["messages"],
            ],
        )
        chat["messages"].append({
            "role": "assistant",
            "content": response.model_dump()["choices"][0]["message"]["content"],
        })
        self._save_chat_history(chat_id)
        self._logger.info(f"Asked question in chat {chat_id}: {question}")
        result = response.model_dump()["choices"][0]["message"]["content"]
        return result



    def _generate_chat_id(self):
        chat_id = str(uuid.uuid4())
        self._active_chats[chat_id] = {
            "created_at": datetime.now(),
            "messages": [],
        }
        self._save_chat_history(chat_id)
        return chat_id


    def _download_chat_history(self, chat_id: str):
        self._logger.info(f"Downloading chat history for chat {chat_id}")
        try:
            chat_data = self._s3_client.read_file(
                bucket_name="hackathon-ai-tech",
                object_key=f"chats/driving_exam/{chat_id}.json"
            )
            chat_data = json.loads(chat_data.read().decode('utf-8'))
            self._active_chats[chat_id] = {
                "created_at": datetime.fromisoformat(chat_data["created_at"]),
                "messages": chat_data["messages"],
            }
            self._logger.info(f"Chat history for {chat_id} downloaded successfully.")
        except Exception as e:
            self._logger.error(f"Failed to download chat history for {chat_id}: {e}")


    def _save_chat_history(self, chat_id: str):
        self._logger.info(f"Saving chat history for chat {chat_id}")
        chat = self._active_chats.get(chat_id)
        if not chat:
            self._logger.warning(f"No chat found with ID {chat_id}")
            return
        chat_data = {
            "created_at": chat["created_at"].isoformat(),
            "messages": chat["messages"],
        }

        self._s3_client.write_file(
            bucket_name="hackathon-ai-tech",
            object_key=f"chats/driving_exam/{chat_id}.json",
            byte_reader=json.dumps(chat_data).encode('utf-8')
        )
        self._logger.info(f"Chat history for {chat_id} saved successfully.")



if __name__ == "__main__":
    from dotenv import load_dotenv, find_dotenv
    import os
    load_dotenv(find_dotenv())
    from clients.role_assumer_client import AWSRoleAssumer

    mistral_api_key = os.getenv("MISTRAL_API_KEY")
    mistral_client = Mistral(api_key=mistral_api_key)

    role_arn = os.getenv("AWS_ROLE_ARN")
    aws_role_assumer = AWSRoleAssumer(role_arn, rotation_minutes=30)
    s3_client = AWSS3Client(aws_role_assumer)
    driving_exam_chat_controller = DrivingExamChatController(mistral_client, s3_client)
    image_url = "https://scontent-fra5-1.xx.fbcdn.net/m1/v/t6/An8VfU1elhSR-EoNnfkcTtYmbqdsUXLdV-KiOurtBYyTo5r1RvWYbnfcmXJt0oxSpC0_WR0-WYjwfC-STC11gDFelSRCg_4NdOZH9cEFOKJg38x3ixssusoCmZCedVdhG5u8hU1eLBTSdgqdsIGpRw?stp=s2048x1151&edm=AOnQwmMEAAAA&_nc_gid=19kZVX5LNKqMignc-RbSlg&_nc_oc=AdmxvGGV8N0qZGtbOSftXPEyePGvyKotDvhh9tB7pA1fNgiWbSQqV7T24uMBHztRCQhjEb0ZghlL9RWWPZ7AU0sw&ccb=10-5&oh=00_AfIgMDbnZ4J-ygCC_eUU8wUYGhpcHAZpyVn1Tp02cH6jqQ&oe=68592EEB&_nc_sid=201bca"
    chat_id, response = driving_exam_chat_controller.generate_driving_questions_for_image(image_url, city="Paris")
    follow_up_response = driving_exam_chat_controller.ask_followup_question("But can't I park there if it is only very shortly and I make sure bycicles can still pass?", chat_id=chat_id)
    print(follow_up_response)