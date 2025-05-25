import logging
import time
from typing import Optional, List
from upstash_vector import Index, Vector
from mistralai import Mistral

class SimilaritySearchController:

    def __init__(self, index_url: str, api_key: str, mistral_client: Mistral, logger: Optional[logging.Logger]) -> None:
        self._index = Index(url=index_url, token=api_key)
        self._mistral = mistral_client
    

    def add_question(self, question_id: str, question: str, image_url: str) -> None:
        res = self._mistral.embeddings.create(
        model="mistral-embed",
        inputs=[question],
        )
        embedding = res.data[0].embedding
        self._index.upsert(
            vectors=[
                Vector(
                    id=question_id,
                    vector=embedding,
                    metadata={
                        "image_url": image_url,
                        "question": question
                    }
                )
            ]
        )
        time.sleep(2)
    

    def search(self, query: str, top_k: int = 5) -> List[str]:
        res = self._mistral.embeddings.create(
            model="mistral-embed",
            inputs=[query],
        )
        embedding = res.data[0].embedding
        results = self._index.query(
            vector=embedding,
            top_k=top_k,
            include_metadata=True
        )
        time.sleep(2)
        return [
            result.metadata["image_url"] for result in results
        ]
    

    def delete_question(self, question_id: str) -> None:
        self._index.delete(ids=[question_id])
        time.sleep(2)


if __name__ == "__main__":

    from dotenv import load_dotenv, find_dotenv
    import os
    load_dotenv(find_dotenv())

    index_url = os.getenv("VECTOR_DB_ENDPOINT")
    api_key = os.getenv("VECTOR_DB_API_KEY")
    mistral_api_key = os.getenv("MISTRAL_API_KEY")
    mistral_client = Mistral(api_key=mistral_api_key)

    sim_search_controller = SimilaritySearchController(
        index_url=index_url,
        api_key=api_key,
        mistral_client=mistral_client,
        logger=logging.getLogger(__name__)
    )
    print(sim_search_controller.search("What is the speed limit in Paris?"), 1)


