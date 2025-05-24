import { interpretCallback, interpretCity, interpretCountry } from "./interpretators";
import { getOrCreateUser, setUserToFlow, updateUser, User } from "../db/user";
import { sendTelegramMessage } from "../telegram_interactions/interactions";
import { message_templates } from "../types/message_templates";
import { CallbackAnswer, ConversationState, resultTelegramMessage } from "../types/types";
import { err, ok, Result } from "neverthrow";

export class FlowRunner {

    constructor() {
    }
    
private async askForCountry(user: User): Promise<Result<boolean, Error>> {
    const message: resultTelegramMessage = {
      chat_id: user.chat_id,
      text: message_templates.welcome_and_country,
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
    const message: resultTelegramMessage = {
      chat_id: user.chat_id,
      text: message_templates.city,
      parse_mode: "MarkdownV2",
      reply_markup: {
        inline_keyboard: [
          [
            {
              text: "Paris",
              callback_data: "PARIS"
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

    private async startFlow(user: User): Promise<Result<boolean, Error>> {
      return ok(true);
    }

    private async handleMainMenuState(
      user: User,
      callback: CallbackAnswer | null,
    ): Promise<Result<boolean, Error>> {
      if (user.conversationState !== ConversationState.MAIN_MENU) {
        return err(new Error("User is not in MAIN_MENU state"));
      }
      let userToProccess = user;
    
      if (callback !== null) {
        const update = await updateUser(user, interpretCity(callback), interpretCountry(callback));
        if (update.isErr()) {
          return err(new Error("Failed to update user with country"));
        }
        userToProccess = update.value;
      }

      if (!userToProccess.country) {
        const result = await this.askForCountry(user);
        if (result.isErr()) {
          return err(new Error("Failed to ask for country"));
        }
        return ok(true);
      } else if (userToProccess.country && !userToProccess.city) {
        const result = await this.askForCity(user);
        if (result.isErr()) {
          return err(new Error("Failed to ask for city"));
        }
        return ok(true);
      } else if (userToProccess.country && userToProccess.city) {
        const result = await setUserToFlow(user);
        if (result.isErr()) {
          return err(new Error("Failed to set user to FLOW state"));
        }
        const flowResult = await this.startFlow(userToProccess);
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

    public async run(chat_id: number, callback: string | null): Promise<Result<boolean, Error>> {
      const userResult = await getOrCreateUser(chat_id);
      if (userResult.isErr()) {
        return err(new Error("Could not get user by chat_id"));
      }

      let user_choice: CallbackAnswer | null = null;
      if (callback !== null) {
        user_choice = interpretCallback(callback);
      }

      switch (userResult.value.conversationState) {
        case ConversationState.MAIN_MENU:
          return this.handleMainMenuState(userResult.value, user_choice);
        case ConversationState.FLOW:
          return ok(true);
      }
    }
}