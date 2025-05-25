import type { Config } from 'drizzle-kit';
import * as dotenv from 'dotenv';
dotenv.config();

// Parse DATABASE_URL to get individual components
const dbUrl = new URL('postgresql://postgres:postgres@db:5432/telegram_bot');

export default {
  schema: './src/db/schema.ts',
  out: './migrations',
  dialect: 'postgresql',
  dbCredentials: {
    host: dbUrl.hostname,
    port: parseInt(dbUrl.port),
    user: dbUrl.username,
    password: dbUrl.password,
    database: dbUrl.pathname.slice(1),
  }
} satisfies Config; 