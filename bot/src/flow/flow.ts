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
              callback_data: "Paris"
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

    private async handleMainMenuState(
      user: User,
      callback: CallbackAnswer | null,
    ): Promise<Result<boolean, Error>> {
      if (user.conversationState !== ConversationState.MAIN_MENU) {
        return err(new Error("User is not in MAIN_MENU state"));
      }
      let userToProccess = user;

      if (callback !== null) {
        const update = await updateUser(user, interpretCity(callback), interpretCountry(callback), null);
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
        await sendTelegramMessage({
            chat_id: user.chat_id,
            text: message_templates.proccesing_message,
            parse_mode: 'MarkdownV2',
          });
        let flowUser = userToProccess;
        flowUser.conversationState = ConversationState.FLOW;
        const flowResult = await this.handleFlow(userToProccess);
        if (flowResult.isErr()) {
          return err(new Error("Failed to start flow"));
        }
        return ok(true);
      }
      return err(new Error("Unexpected state in handleMainMenuState"));
    }

    private async handleFlow(user: User): Promise<Result<boolean, Error>> {

      const getQuestionImageUrlResult = await getQuestionImageUrl(user.city!);
      if (getQuestionImageUrlResult.isErr()) {
        return err(new Error("Failed to get question image url"));
      }

      console.log("getQuestionImageUrlResult", getQuestionImageUrlResult.value);

      const getQuestionResult = await getQuestion(getQuestionImageUrlResult.value, user.city!);
      if (getQuestionResult.isErr()) {
        return err(new Error("Failed to get question"));
      }

      await updateUser(user, null, null, getQuestionResult.value.explanation);

      console.log("getQuestionResult", getQuestionResult.value);

      // First send the image
      const photoResult = await sendTelegramPhoto(user.chat_id, getQuestionImageUrlResult.value);
      if (photoResult.isErr()) {
        return err(new Error("Failed to send question image"));
      }

      // Then send the question text with choices
        const questionMessage = message_templates.question
        .replace("{question_text}", getQuestionResult.value.question_text)
        .replace("{choice_a}", getQuestionResult.value.choices[0].text)
        .replace("{choice_b}", getQuestionResult.value.choices[1].text)
        .replace("{choice_c}", getQuestionResult.value.choices[2].text)
        .replace("{choice_d}", getQuestionResult.value.choices[3].text)
      const message: resultTelegramMessage = {
        chat_id: user.chat_id,
        text: questionMessage,
        parse_mode: "MarkdownV2",
        reply_markup: {
          inline_keyboard: [
            [
              { text: 'A', callback_data: getQuestionResult.value.choices[0].id},
              { text: 'B', callback_data: getQuestionResult.value.choices[1].id},
            ],
            [
              { text: 'C', callback_data: getQuestionResult.value.choices[2].id},
              { text: 'D', callback_data: getQuestionResult.value.choices[3].id},
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
      const updateCurrentCorrectAnswerIdResult = await updateUserCurrentCorrectAnswerId(user.chat_id, getQuestionResult.value.correct_answer_id);
      if (updateCurrentCorrectAnswerIdResult.isErr()) {
        return err(new Error("Failed to update user with current correct answer id"));
      }

      return ok(true);
    }

    private async handleFlowState(user: User, user_choice: CallbackAnswer | null): Promise<Result<boolean, Error>> {
      const { correct_answer_count, wrong_answer_count, current_correct_answer_id } = user;

      if (user_choice === null) {
        // Send the first question
          await sendTelegramMessage({
            chat_id: user.chat_id,
            text: message_templates.proccesing_message,
            parse_mode: 'MarkdownV2',
          });
        const sendQuestionResult = await this.handleFlow(user);
        if (sendQuestionResult.isErr()) {
          return err(new Error("Failed to send first question"));
        }
        return ok(true);
      }

      console.log("user_choice", user_choice);
      console.log("current_correct_answer_id", current_correct_answer_id);

      if (current_correct_answer_id === user_choice.toString()) {
        // Got the correct answer
        const result = await updateUserCorrectAnswerCount(user.chat_id, correct_answer_count + 1);
        if (result.isErr()) {
          return err(new Error("Failed to update user correct answer count"));
        }

        const sendTelegramMessageResult = await sendTelegramMessage({
          chat_id: user.chat_id,
          text: `🎉 Correct answer!

You got it right ${correct_answer_count + 1} times!

Explanation: ${user.explanation}`,

          parse_mode: "MarkdownV2",
        });
        if (sendTelegramMessageResult.isErr()) {
          return err(new Error("Failed to send message to user that they got the correct answer"));
        }
        await sendTelegramMessage({
            chat_id: user.chat_id,
            text: message_templates.proccesing_message,
            parse_mode: 'MarkdownV2',
          });

      } else {
        // Got the wrong answer
        const result = await updateUserWrongAnswerCount(user.chat_id, wrong_answer_count + 1);
        if (result.isErr()) {
          return err(new Error("Failed to update user wrong answer count"));
        }

        const sendTelegramMessageResult = await sendTelegramMessage({
          chat_id: user.chat_id,
          text: `❌ Wrong answer! You got it wrong ${wrong_answer_count + 1} times!

The correct answer was ${current_correct_answer_id}.

Explanation: ${user.explanation}`,
          parse_mode: "MarkdownV2",
        });
        if (sendTelegramMessageResult.isErr()) {
          return err(new Error("Failed to send message to user that they got the wrong answer"));
        }
        await sendTelegramMessage({
            chat_id: user.chat_id,
            text: message_templates.proccesing_message,
            parse_mode: 'MarkdownV2',
          });
      }
      let sendQuestionResult = await this.handleFlow(user);

      while (sendQuestionResult.isErr()) {
        console.error("Error sending next question:", sendQuestionResult.error);

        await new Promise(resolve => setTimeout(resolve, 500));

        sendQuestionResult = await this.handleFlow(user);
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