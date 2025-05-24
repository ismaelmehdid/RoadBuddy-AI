import { getOrCreateUser, User } from "./server/db/user";
import { ConversationState, TelegramMessage } from "./types/types";
import { err, ok, Result } from "neverthrow";

export class FlowRunner {

    constructor() {
    }

    // New conversation means user not found so we are creating a new user
    public async newConversation(message: TelegramMessage): Promise<Result<User, Error>> {
      const createUserResult = await getOrCreateUser(message.chat.id);
      if (createUserResult.isErr()) {
        return err(new Error("User not created"));
      }
      return ok(createUserResult.value);
    }

    private async handleUnspecifiedState(chat_id: string): Promise<Result<void, Error>> {
      const userResult = await getUserByChatId(chat_id);
      if (userResult.isErr()) {
        return err(new Error("User not found"));
      }
      return ok(undefined);
    }

    private async handleMainMenuState(user: User): Promise<Result<void, Error>> {
      // Check if we have city in db
      // If not, ask for city
      // If yes, ask for country
      // If country is not France, ask for country



      return ok(undefined);
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

    public async run(message: TelegramMessage): Promise<Result<boolean, Error>> {
      const userResult = await getOrCreateUser(message.chat.id);
      if (userResult.isErr()) {
        return err(new Error("Could not get user by chat_id"));
      }

      switch (userResult.value.conversationState) {
        case ConversationState.MAIN_MENU:
          return this.handleMainMenuState();
        case ConversationState.FLOW:
          return ok(true);
      }
    }
}