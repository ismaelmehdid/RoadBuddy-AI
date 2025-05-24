import { z } from "zod";

export enum ConversationState {
  UNSPECIFIED = "UNSPECIFIED",
  MAIN_MENU = "MAIN_MENU",
  FLOW = "FLOW",
}

export enum Countries {
    FRANCE = "FRANCE",
}

export enum City {
    PARIS = "PARIS",
}

export const TelegramMessageSchema = z.object({
  message_id: z.number(),
  from: z.object({
    id: z.number(),
    is_bot: z.boolean(),
    first_name: z.string(),
    username: z.string().optional(),
    language_code: z.string().optional(),
  }),
  chat: z.object({
    id: z.number(),
    first_name: z.string().optional(),
    username: z.string().optional(),
    type: z.enum(['private', 'group', 'supergroup', 'channel']),
  }),
  date: z.number(),
  text: z.string(),
  entities: z.array(z.any()).optional(),
});

export type TelegramMessage = z.infer<typeof TelegramMessageSchema>;

export const AnswerTelegramMessageSchema = z.object({
  chat_id: z.number(),
  text: z.string(),
  image_url: z.string(),
});

export type AnswerTelegramMessage = z.infer<typeof AnswerTelegramMessageSchema>;