import { resultTelegramMessage } from '@/types/types';
import { err, ok, Result } from 'neverthrow'

export async function sendTelegramMessage(message: resultTelegramMessage): Promise<Result<boolean, Error>> {
  const token = process.env.TELEGRAM_TOKEN;
  if (!token) {
    console.error('TELEGRAM_TOKEN not set');
    return err(new Error('TELEGRAM_TOKEN not set'));
  }

  const response = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(message ),
  });

  const data = await response.json();
  if (!data.ok) {
    console.error('Telegram API error:', data);
    return err(new Error(`Telegram API error: ${data.description}`));
  }

  return ok(true);
}