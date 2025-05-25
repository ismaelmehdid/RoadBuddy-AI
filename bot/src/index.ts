import express from 'express';
import bodyParser from 'body-parser';
import { Telegraf } from 'telegraf';
import { FlowRunner } from './flow/flow';
import { CallbackQuerySchema, InputTelegramMessageSchema } from './types/types';
import dotenv from 'dotenv';
import { Pool } from 'pg';
import { drizzle } from 'drizzle-orm/node-postgres';
import { migrate } from 'drizzle-orm/node-postgres/migrator';
import { sendTelegramMessage } from './telegram_interactions/interactions';
import { message_templates } from './types/message_templates';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.BOT_PORT;
const TELEGRAM_TOKEN = process.env.TELEGRAM_TOKEN;
const WEBHOOK_URL = process.env.WEBHOOK_URL;
const DATABASE_URL = process.env.DATABASE_URL;

if (!TELEGRAM_TOKEN) {
  throw new Error('TELEGRAM_TOKEN is not defined in environment variables');
}

if (!WEBHOOK_URL) {
  throw new Error('WEBHOOK_URL is not defined in environment variables');
}

if (!DATABASE_URL) {
  throw new Error('DATABASE_URL is not defined in environment variables');
}

const pool = new Pool({
  connectionString: DATABASE_URL,
});

// Initialize database instance
export const db = drizzle(pool);

// Initialize bot and flow runner
const bot = new Telegraf(TELEGRAM_TOKEN);
const flowRunner = new FlowRunner();

// Handle text messages
bot.on('text', async (ctx) => {
  const text = ctx.message.text;

  console.log('Received message:', text);

  const message = InputTelegramMessageSchema.safeParse(ctx.message);
  if (!message.success) {
    console.error('Invalid message format:', message.error);
    return ctx.reply('Invalid message format');
  }

  let result;
    if (message.data.text === '/back_to_main_menu' || message.data.text === '/show_score') {
        result = await flowRunner.handleSpecialCommands(message.data.chat.id, message.data.text);
    } else {
        result = await flowRunner.run(message.data.chat.id, null);
    }

  if (result.isErr()) {
    console.error('Error processing message:', result.error);
    return ctx.reply('Error processing your request.');
  }
});

// Handle callback queries
bot.on('callback_query', async (ctx) => {
  const callbackQuery = ctx.callbackQuery;
  console.log('Received callback query:', callbackQuery);

  try {
    await ctx.answerCbQuery('Processing...');
  } catch (err) {
    console.warn('Failed to answer callback query in time:', err);
  }

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
});

// Set up webhook
async function setupWebhook() {
  try {
    const webhookUrl = `${WEBHOOK_URL}/webhook`;
    console.log(`Setting up webhook at: ${webhookUrl}`);
    
    await bot.telegram.setWebhook(webhookUrl);
    console.log('Webhook set up successfully!');
  } catch (error) {
    console.error('Error setting up webhook:', error);
  }
}

// Middleware
app.use(bodyParser.json());

// Webhook endpoint
app.post('/webhook', async (req: any, res: any) => {
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
});

// Start the server
app.listen(PORT, async () => {
  console.log(`Server running on port ${PORT}`);
  
  try {
    // Run migrations
    console.log('Running database migrations...');
    await migrate(db, { migrationsFolder: './migrations' });
    console.log('Database migrations completed successfully');
    
    // Set up webhook
    await setupWebhook();
  } catch (error) {
    console.error('Error during startup:', error);
    process.exit(1);
  }
});
