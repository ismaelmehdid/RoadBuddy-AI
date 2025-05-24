import requests
from shared


class MistalClient:
    def __init__(self, api_key: str):
        self._api_key = api_key
    

    def chat_completion(self, messages: list, model: str = "pixtral-12b"):
        """
        Sends a chat completion request to the Mistral API.
        
        :param messages: List of messages in the conversation.
        :param model: The model to use for the chat completion.
        :return: The response from the Mistral API.
        """
        url = "https://api.mistral.ai/v1/chat/completions"

        self.headers = {
            "Authorization
API_KEY = "your_api_key_here"
API_URL = "https://api.mistral.ai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "pixtral-12b",
    "messages": [
        {"role": "user", "content": [
            {"type": "text", "content": "What is happening in this image?"},
            {"type": "image", "url": "https://example.com/image.jpg"}
        ]}
    ]
}

response = requests.post(API_URL, json=payload, headers=headers)
print(response.json())