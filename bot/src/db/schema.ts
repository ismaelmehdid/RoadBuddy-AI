import { text } from "body-parser";
import { City, ConversationState, Countries } from "../types/types";
import { bigint, integer, pgEnum, pgTable, varchar } from "drizzle-orm/pg-core";

export function enumToPgEnum<T extends Record<string, any>>(
  myEnum: T,
): [T[keyof T], ...T[keyof T][]] {
  return Object.values(myEnum).map((value: any) => `${value}`) as any;
}

export const conversationState = pgEnum(
  'ConversationState',
  enumToPgEnum(ConversationState),
);

export const userCity = pgEnum(
  'userCity',
  enumToPgEnum(City),
);

export const userCountry = pgEnum(
  'userCountry',
  enumToPgEnum(Countries),
);

export const usersTable = pgTable("users", {
  id: integer().primaryKey().generatedAlwaysAsIdentity(),
  chat_id: bigint("chat_id", { mode: "number" }).notNull(),
  conversationState: conversationState('conversationState').default(
      ConversationState.MAIN_MENU,
    ),
  wrong_answer_count: integer("wrong_answer_count").default(0),
  correct_answer_count: integer("correct_answer_count").default(0),
  current_correct_answer_id: varchar("current_correct_answer_id", { length: 1 }).default(''),
  city: userCity('city'),
  country: userCountry('country'),
  explanation: varchar("explanation", { length: 2048 }).default(''),
});