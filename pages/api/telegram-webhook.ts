'use server';
import { FlowRunner } from '@/flowRunner';
import { CallbackQuerySchema, InputTelegramMessageSchema } from '@/types/types';
import { NextApiRequest, NextApiResponse } from 'next';
import { Markup, Telegraf } from 'telegraf';

const token = process.env.TELEGRAM_TOKEN;
if (!token) {
  throw new Error('TELEGRAM_TOKEN is not set in environment variables');
}
const bot = new Telegraf(token);

const flowRunner = new FlowRunner();

bot.on('text', async (ctx) => {
  const text = ctx.message.text;

  console.log('Received message:', text);

  const message = InputTelegramMessageSchema.safeParse(ctx.message);
  if (!message.success) {
    console.error('Invalid message format:', message.error);
    return ctx.reply('Invalid message format');
  }

  const result = await flowRunner.run(message.data.chat.id, null);

  if (result.isErr()) {
    console.error('Error processing message:', result.error);
    return ctx.reply('Error processing your request.');
  }
});

bot.on('callback_query', async (ctx) => {
  const callbackQuery = ctx.callbackQuery;
  
  console.log('Received callback query:', callbackQuery);

  const message = CallbackQuerySchema.safeParse(callbackQuery);
  if (!message.success) {
    console.error('Invalid message format:', message.error);
    return ctx.reply('Invalid reply format');
  } else {
    console.log('Valid callback query:', message.data);
  }
    const result = await flowRunner.run(message.data.message.chat.id, message.data.data);
  if (result.isErr()) {
    console.error('Error processing message:', result.error);
    return ctx.reply('Error processing your request.');
  }
    ctx.answerCbQuery('Processing your request...');
});

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    const update = req.body;

    console.log('Received update:', update);

    try {
      await bot.handleUpdate(update);
      return res.status(200).send('Message processed successfully');
    } catch (error) {
      console.error('Error processing message:', error);
      return res.status(500).send('Error processing message');
    }
  } else {
    res.status(405).send('Method Not Allowed');
  }
}
