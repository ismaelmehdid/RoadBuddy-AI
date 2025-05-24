import { getOrCreateUser, setUserToFlow, setUserToMainMenu, updateUser, updateUserCorrectAnswerCount, updateUserCurrentCorrectAnswerId, updateUserWrongAnswerCount, User } from "../db/user";
import { sendTelegramMessage, sendTelegramPhoto } from "../telegram_interactions/interactions";
import { getQuestion, getQuestionImageUrl } from "../telegram_interactions/question";
import { message_templates } from "../types/message_templates";
import { CallbackAnswer, ConversationState, Question, resultTelegramMessage } from "../types/types";
import { interpretCallback, interpretCity, interpretCountry } from "./interpretators";
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

    private async sendQuestion(user: User): Promise<Result<boolean, Error>> {

      const getQuestionImageUrlResult = await getQuestionImageUrl(user.city!);
      if (getQuestionImageUrlResult.isErr()) {
        return err(new Error("Failed to get question image url"));
      }

      console.log("getQuestionImageUrlResult", getQuestionImageUrlResult.value);

      const getQuestionResult = await getQuestion(getQuestionImageUrlResult.value, user.city!);
      if (getQuestionResult.isErr()) {
        return err(new Error("Failed to get question"));
      }

      console.log("getQuestionResult", getQuestionResult.value);

      // First send the image
      const photoResult = await sendTelegramPhoto(user.chat_id, getQuestionImageUrlResult.value);
      if (photoResult.isErr()) {
        return err(new Error("Failed to send question image"));
      }

      // Then send the question text with choices
      const message: resultTelegramMessage = {
        chat_id: user.chat_id,
        text: `🔍 ${getQuestionResult.value.question_text}`,
        parse_mode: "MarkdownV2",
        reply_markup: {
          inline_keyboard: [
            [
              { text: getQuestionResult.value.choices[0].text, callback_data: String(getQuestionResult.value.choices[0].id) },
              { text: getQuestionResult.value.choices[1].text, callback_data: String(getQuestionResult.value.choices[1].id) },
            ],
            [
              { text: getQuestionResult.value.choices[2].text, callback_data: String(getQuestionResult.value.choices[2].id) },
              { text: getQuestionResult.value.choices[3].text, callback_data: String(getQuestionResult.value.choices[3].id) },
            ],
          ],
        },
      }

      const result = await sendTelegramMessage(message);
      if (result.isErr()) {
        console.log("result", result);
        return err(new Error("Failed to send question"));
      }

      // Update current correct answer id
      const updateCurrentCorrectAnswerIdResult = await updateUserCurrentCorrectAnswerId(user.chat_id, getQuestionResult.value.correct_answer_id.toString());
      if (updateCurrentCorrectAnswerIdResult.isErr()) {
        return err(new Error("Failed to update user with current correct answer id"));
      }

      return ok(true);
    }

    private async handleFlowState(user: User, user_choice: CallbackAnswer | null): Promise<Result<boolean, Error>> {
      const { correct_answer_count, wrong_answer_count, current_correct_answer_id } = user;

      if (user_choice === null) {
        // Send the first question
        const sendQuestionResult = await this.sendQuestion(user);
        if (sendQuestionResult.isErr()) {
          return err(new Error("Failed to send first question"));
        }
        return ok(true);
      }

      console.log("user_choice", user_choice);
      console.log("current_correct_answer_id", current_correct_answer_id);

      if (current_correct_answer_id === user_choice) {
        // Got the correct answer
        const result = await updateUserCorrectAnswerCount(user.chat_id, correct_answer_count + 1);
        if (result.isErr()) {
          return err(new Error("Failed to update user correct answer count"));
        }

        const sendTelegramMessageResult = await sendTelegramMessage({
          chat_id: user.chat_id,
          text: `🎉 Correct answer\\! You got it right ${correct_answer_count + 1} times\\!`,
          parse_mode: "MarkdownV2",
        });
        if (sendTelegramMessageResult.isErr()) {
          return err(new Error("Failed to send message to user that they got the correct answer"));
        }

      } else {
        // Got the wrong answer
        const result = await updateUserWrongAnswerCount(user.chat_id, wrong_answer_count + 1);
        if (result.isErr()) {
          return err(new Error("Failed to update user wrong answer count"));
        }

        const sendTelegramMessageResult = await sendTelegramMessage({
          chat_id: user.chat_id,
          text: `❌ Wrong answer\\! You got it wrong ${wrong_answer_count + 1} times\\! The correct answer was ${current_correct_answer_id}`,
          parse_mode: "MarkdownV2",
        });
        if (sendTelegramMessageResult.isErr()) {
          return err(new Error("Failed to send message to user that they got the wrong answer"));
        }
      }

      const sendQuestionResult = await this.sendQuestion(user);
      if (sendQuestionResult.isErr()) {
        return err(new Error("Failed to send next question"));
      }

      return ok(true);
    }

    public async handleSpecialCommands(
      chat_id: number,
      specialCommand: '/back_to_main_menu' | '/show_score',
    ): Promise<Result<boolean, Error>> {
      const userResult = await getOrCreateUser(chat_id);
      if (userResult.isErr()) {
        return err(new Error("Could not get user by chat_id"));
      }

      const user = userResult.value;
      if (specialCommand === '/back_to_main_menu') {
        const result = await setUserToMainMenu(user);
        if (result.isErr()) {
          return err(new Error("Failed to set user to MAIN_MENU state"));
        }
        this.askForCountry(user);
        return ok(true);
      } else if (specialCommand === '/show_score') {
        this.showScore(user);
        return ok(true);
      }
      return err(new Error("Unknown special command"));
    }

    private async showScore(user: User): Promise<Result<boolean, Error>> {
      const scoreMessage = message_templates.score
        .replace("{correct_answer_count}", user.correct_answer_count.toString())
        .replace("{wrong_answer_count}", user.wrong_answer_count.toString())

      const message: resultTelegramMessage = {
        chat_id: user.chat_id,
        text: scoreMessage,
        parse_mode: "MarkdownV2",
      }
      const result = await sendTelegramMessage(message);
      if (result.isErr()) {
        return err(new Error("Failed to send score message"));
      }
      return ok(true);
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
          return this.handleFlowState(userResult.value, user_choice);
      }
    }
}