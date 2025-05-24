import { err, ok, Result } from 'neverthrow';
import { db } from './index';
import { usersTable } from './schema';
import { ConversationState } from '@/types/types';
import { eq } from 'drizzle-orm';

export interface CreateUserInput {
  chat_id: string;
  conversationState?: ConversationState;
  wrong_answer_count?: number;
  correct_answer_count?: number;
  current_correct_answer_id?: string;
}

export interface User {
  chat_id: string;
  conversationState: ConversationState;
  wrong_answer_count: number;
  correct_answer_count: number;
  current_correct_answer_id: string;
}


export async function createUser(input: CreateUserInput): Promise<Result<void, Error>> {
  try {
    // Check if user already exists
    const existingUser = await db
      .select()
      .from(usersTable)
      .where(eq(usersTable.chat_id, input.chat_id))
      .limit(1);

    if (existingUser.length > 0) {
      return ok(undefined);
    }

    // Create new user
    const [newUser] = await db
      .insert(usersTable)
      .values({
        chat_id: input.chat_id,
        conversationState: input.conversationState || ConversationState.UNSPECIFIED,
        wrong_answer_count: input.wrong_answer_count || 0,
        correct_answer_count: input.correct_answer_count || 0,
        current_correct_answer_id: input.current_correct_answer_id || '',
      })
      .returning();

    return ok(undefined);
  } catch (error) {
    console.error('Error creating user:', error);
    throw new Error('Failed to create user');
  }
}

export async function getUserByChatId(chat_id: string): Promise<Result<User, Error>> {
  try {
    const user = await db.select().from(usersTable).where(eq(usersTable.chat_id, chat_id)).limit(1);
    return ok(user[0] as User);
  } catch (error) {
    return err(new Error('Failed to get user by chat_id'));
  }
}