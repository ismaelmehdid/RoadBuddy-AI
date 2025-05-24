import { err, ok, Result } from 'neverthrow';
import { db } from './index';
import { usersTable } from './schema';
import { City, ConversationState, Countries } from '@/types/types';
import { eq } from 'drizzle-orm';

export interface User {
  chat_id: number;
  conversationState: ConversationState;
  wrong_answer_count: number;
  correct_answer_count: number;
  current_correct_answer_id: string;
  city:  City | null;
  country:  Countries | null;

}

export async function getOrCreateUser(chat_id: number): Promise<Result<User, Error>> {
  try {
    // Check if user already exists
    const existingUser = await db
      .select()
      .from(usersTable)
      .where(eq(usersTable.chat_id, chat_id))
      .limit(1)

    if (existingUser.length > 0) {
      return ok(existingUser[0] as User);
    }

    const [newUser] = await db
      .insert(usersTable)
      .values({
        chat_id: chat_id,
        conversationState: ConversationState.MAIN_MENU,
        wrong_answer_count: 0,
        correct_answer_count:  0,
        current_correct_answer_id: '',
        city: null,
        country: null,
      })
      .returning();

    return ok(newUser as User);
  } catch (error) {
    console.error('Error creating user:', error);
    throw new Error('Failed to create user');
  }
}