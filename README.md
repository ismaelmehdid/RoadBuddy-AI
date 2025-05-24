# RoadBuddy AI

A Telegram chatbot that teaches driving theory with real street photos from your own city, one quick quiz at a time.

## Features

* **Hyper-local quizzes**: Uses Mapillary street-level images of the user’s city
* **Multimodal LLM**: GPT-4o Vision generates a 3-option multiple-choice question and a one-sentence explanation
* **Snackable learning**: Each quiz round takes less than 60 seconds
* **Zero setup**: Everything runs in Telegram—no extra apps needed

## Tech Stack

* **Bot**: Telegram Bot API with `aiogram` (Python)
* **Images**: Mapillary REST API
* **LLM**: OpenAI GPT-4o Vision (fallback: Google Gemini)
* **Backend**: FastAPI on Render
* **Storage**: SQLite (in-memory)

## Getting Started

1. **Clone the repo**

   ```bash
   git clone https://github.com/yvann-ba/RoadBuddy-AI
   cd RoadBuddy-AI
   ```

## Roadmap

* ✅ MVP: single-country support, random quizzes
* 🔲 Caching of images & Q/A pairs
* 🔲 Adaptive difficulty based on user performance
* 🔲 Audio explanations via ElevenLabs TTS
