import type { Config } from 'drizzle-kit';
import * as dotenv from 'dotenv';
dotenv.config();

if (!process.env.DATABASE_URL) {
  throw new Error('DATABASE_URL is not defined');
}

// Parse DATABASE_URL to get individual components
const dbUrl = new URL(process.env.DATABASE_URL);

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