# RoadBuddy AI

A Telegram chatbot that teaches driving theory with real street photos from your own city, one quick quiz at a time.

## Features

- **Hyper-local quizzes**: Utilizes Mapillary street-level images from the user’s city.
- **Multimodal LLM**: Mistral AI generates a multiple-choice question with 3 options and a one-sentence explanation.
- **Infinite learning**: You can process an infinite number of completely unique questions.
- **Zero setup**: Everything runs directly in Telegram—no additional apps required.

## Tech Stack

- **Bot**: Telegram Bot API with Telegraf SDK
- **Images**: Mapillary REST API
- **LLM**: Mistral AI
- **Backend**: Express on TypeScript
- **Storage**: PostgreSQL DB

## Dependencies

   - Docker
   - Ngrok
     
## Getting Started

1. **Clone the repo**

   ```bash
   git clone https://github.com/yvann-ba/RoadBuddy-AI
   cd RoadBuddy-AI
   ```
2. **Setup ngrok**
   ```bash
   ngrok htpp 3000
   ```
   <img width="821" alt="Screenshot 2025-05-24 at 20 36 55" src="https://github.com/user-attachments/assets/590ac93b-2779-43ec-b1af-bedeb65366d0" />

   Copy your URL to setup env

3. **Ask me to get TELEGRAM_TOKEN or create your own**

   It’s better to use our existing [bot](https://t.me/road_buddy_ai_bot)since it already has an avatar, description, and other details. If you create your own bot, it will be fully functional but will appear as a blank bot.
   
   For any questions or assistance, feel free to reach out to me:
   - **LinkedIn**: [Andrii Syvash](https://www.linkedin.com/in/asyvash/)
   - **Email**: [asyvash.work.it@gmail.com](mailto:asyvash.work.it@gmail.com)
   
   To create your own bot, simply follow these steps:
   1. Message [@BotFather](https://t.me/BotFather) on Telegram with the command **/newbot**.
   2. Follow the prompts to provide the necessary information.
   3. Once done, you’ll receive a token like this: `7899634355:AAH21k1iAJuw4UyCLBXQo80zkvuqJ0f89WQ` (note: this is just an example and not real data).
  
3. **Create .env file using this template**

   ```bash
   POSTGRES_DB=telegram_bot
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
   
   TELEGRAM_TOKEN=
   BOT_PORT=3000
   WEBHOOK_URL=
   ```
   where WEBHOOK_URL is your ngok url.

4. **Almost ready to start!**

   If you followed all the steps correctly, run the final command to start the project:

   ```bash
      ./setup.sh start
   ```

## Potential bussiness model:

   - We can limit daily messages to 10. After that, users will need to purchase a subscription.
   - A perfect solution for passing the driving exam, as you will practice with real images from your city.
