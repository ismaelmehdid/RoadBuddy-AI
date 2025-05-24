import { z } from "zod";

export enum ConversationState {
  MAIN_MENU = "MAIN_MENU",
  FLOW = "FLOW",
}

export enum Countries {
    FRANCE = "FRANCE",
}

export enum City {
    PARIS = "PARIS",
}

export const InputTelegramMessageSchema = z.object({
  message_id: z.number().optional(),
  from: z.object({
    id: z.number(),
    first_name: z.string(),
    username: z.string().optional(),
  }),
  chat: z.object({
    id: z.number(),
    type: z.enum(['private', 'group', 'supergroup', 'channel']),
  }),
  date: z.number(),
  text: z.string().optional(),
  callback_query: z
    .object({
      id: z.string(),
      from: z.object({
        id: z.number(),
        first_name: z.string(),
        username: z.string().optional(),
      }),
      data: z.string(),
    })
    .optional(),
});

export type inputTelegramMessage = z.infer<typeof InputTelegramMessageSchema>;

const InlineKeyboardButtonSchema = z.object({
  text: z.string(),
  callback_data: z.string(),
});

const InlineKeyboardMarkupSchema = z.object({
  inline_keyboard: z.array(z.array(InlineKeyboardButtonSchema)),
});

const SendMessageWithInlineSchema = z.object({
  chat_id: z.number(),
  text: z.string(),
  parse_mode: z.string().optional(),
  reply_markup: InlineKeyboardMarkupSchema,
});

export type resultTelegramMessage = z.infer<typeof SendMessageWithInlineSchema>;