import { createUser, getUserByChatId, User } from "./server/db/user";
import { ConversationState } from "./types/types";
import { err, ok, Result } from "neverthrow";

interface Message {
  chat_id: string;
  user_id: number;
  message: string; // Should be an event type
}

export class FlowRunner {

    constructor() {
    }

    public async startFlow(message: Message): Promise<Result<void, Error>> {
      const createUserResult = await createUser({ chat_id: message.chat_id });
      if (createUserResult.isErr()) {
        return err(new Error("User not created"));
      }
      return ok(undefined);
    }
    
    private async handleUnspecifiedState(chat_id: string): Promise<Result<void, Error>> {
      const userResult = await getUserByChatId(chat_id);
      if (userResult.isErr()) {
        return err(new Error("User not found"));
      }
      return ok(undefined);
    }

    private async handleMainMenuState(chat_id: string): Promise<Result<void, Error>> {
      const userResult = await getUserByChatId(chat_id);
      if (userResult.isErr()) {
        return err(new Error("User not found"));
      }
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

    public async run(message: Message): Promise<Result<void, Error>> {
      const userResult = await getUserByChatId(message.chat_id);
      if (userResult.isErr()) { // means user not found
        return this.startFlow(message);
      }

      switch (userResult.value.conversationState) {
        case ConversationState.MAIN_MENU:
          
          return ok(undefined);
        case ConversationState.FLOW:


      }

      const user = userResult.value;

      return ok(undefined);
    }
}