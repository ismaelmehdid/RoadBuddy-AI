import { getOrCreateUser, setUserToFlow, User } from "./server/db/user";
import { sendTelegramMessage } from "./telegram_interactions/interactions";
import { ConversationState, inputTelegramMessage, resultTelegramMessage } from "./types/types";
import { err, ok, Result } from "neverthrow";

export class FlowRunner {

    constructor() {
    }
    
private async askForCountry(user: User): Promise<Result<boolean, Error>> {
    const message: resultTelegramMessage = {
      chat_id: user.chat_id,
      text: `
        🚗 **Welcome to RoadBuddy AI**  
        I will help you master driving rules 🌍  
        To get started, please select your **country** below:  
        
        🏁 Choose your country and let's begin your driving journey 👇
      `,
      parse_mode: "MarkdownV2",
      reply_markup: {
        inline_keyboard: [
          [
            {
              text: "🇫🇷 France",
              callback_data: "FRANCE"
            }
          ],
        ]
      }
    };

    const result = await sendTelegramMessage(message);
    if (result.isErr()) {
      return err(new Error("Failed to send message asking for country"));
    }

    return ok(true);
  }


    private async askForCity(user: User): Promise<Result<boolean, Error>> {
      return ok(true);
    }

    private async startFlow(user: User): Promise<Result<boolean, Error>> {
      return ok(true);
    }

    private async handleMainMenuState(
      user: User,
      message: inputTelegramMessage
    ): Promise<Result<boolean, Error>> {
      if (user.conversationState !== ConversationState.MAIN_MENU) {
        return err(new Error("User is not in MAIN_MENU state"));
      }
      if (!user.country) {
        const result = await this.askForCountry(user);
        if (result.isErr()) {
          return err(new Error("Failed to ask for country"));
        }
        return ok(true);
      } else if (user.country && !user.city) {
        const result = await this.askForCity(user);
        if (result.isErr()) {
          return err(new Error("Failed to ask for city"));
        }
        return ok(true);
      } else if (user.country && user.city) {
        const result = await setUserToFlow(user);
        if (result.isErr()) {
          return err(new Error("Failed to set user to FLOW state"));
        }
        const flowResult = await this.startFlow(user);
        if (flowResult.isErr()) {
          return err(new Error("Failed to start flow"));
        }
        return ok(true);
      }
      return err(new Error("Unexpected state in handleMainMenuState"));
    }

    private async handleFlowState(user: User): Promise<Result<void, Error>> {
      const { chat_id, conversationState, wrong_answer_count, correct_answer_count, current_correct_answer_id } = user;

      if (conversationState === ConversationState.FLOW) {
        return ok(undefined);
      }

      if (conversationState === ConversationState.MAIN_MENU) {
        return ok(undefined);
      }

      return ok(undefined);
    }

    public async run(message: inputTelegramMessage): Promise<Result<boolean, Error>> {
      const userResult = await getOrCreateUser(message.chat.id);
      if (userResult.isErr()) {
        return err(new Error("Could not get user by chat_id"));
      }

      switch (userResult.value.conversationState) {
        case ConversationState.MAIN_MENU:
          return this.handleMainMenuState(userResult.value, message);
        case ConversationState.FLOW:
          return ok(true);
      }
    }
}