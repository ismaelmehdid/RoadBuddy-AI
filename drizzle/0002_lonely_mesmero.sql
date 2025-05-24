CREATE TYPE "public"."ConversationState" AS ENUM('UNSPECIFIED', 'MAIN_MENU', 'FLOW', 'STOPPED');--> statement-breakpoint
ALTER TABLE "users" DROP CONSTRAINT "users_email_unique";--> statement-breakpoint
ALTER TABLE "users" ADD COLUMN "phone_number" varchar(15) NOT NULL;--> statement-breakpoint
ALTER TABLE "users" ADD COLUMN "conversationState" "ConversationState" DEFAULT 'UNSPECIFIED';--> statement-breakpoint
ALTER TABLE "users" ADD COLUMN "wrong_answer_count" integer DEFAULT 0;--> statement-breakpoint
ALTER TABLE "users" ADD COLUMN "correct_answer_count" integer DEFAULT 0;--> statement-breakpoint
ALTER TABLE "users" ADD COLUMN "current_correct_answer_id" varchar(1) DEFAULT '';--> statement-breakpoint
ALTER TABLE "users" DROP COLUMN "firstName";--> statement-breakpoint
ALTER TABLE "users" DROP COLUMN "lastName";--> statement-breakpoint
ALTER TABLE "users" DROP COLUMN "email";