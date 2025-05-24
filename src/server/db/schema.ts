import { ConversationState } from "@/types/types";
import { integer, pgEnum, pgTable, varchar } from "drizzle-orm/pg-core";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function enumToPgEnum<T extends Record<string, any>>(
  myEnum: T,
): [T[keyof T], ...T[keyof T][]] {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return Object.values(myEnum).map((value: any) => `${value}`) as any;
}

export const conversationState = pgEnum(
  'ConversationState',
  enumToPgEnum(ConversationState),
);

export const usersTable = pgTable("users", {
  id: integer().primaryKey().generatedAlwaysAsIdentity(),
  chat_id: varchar("chat_id", { length: 15 }).notNull(),
  conversationState: conversationState('conversationState').default(
      ConversationState.UNSPECIFIED,
    ),
  wrong_answer_count: integer("wrong_answer_count").default(0),
  correct_answer_count: integer("correct_answer_count").default(0),
  current_correct_answer_id: varchar("current_correct_answer_id", { length: 1 }).default(''),
});