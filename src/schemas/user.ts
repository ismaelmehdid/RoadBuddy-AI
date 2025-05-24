import { z } from "zod";
import { ConversationState } from "../types/types";

export const userSchema = z.object({
  id: z.number(),
  chat_id: z.number(),
  conversationState: z.nativeEnum(ConversationState).default(ConversationState.UNSPECIFIED),
  wrong_answer_count: z.number().nullable().default(0),
  correct_answer_count: z.number().nullable().default(0),
  current_correct_answer_id: z.string().nullable().default(""),
});

export type User = z.infer<typeof userSchema>;

export const createUserSchema = userSchema.omit({ id: true });
export type CreateUserInput = z.infer<typeof createUserSchema>; 