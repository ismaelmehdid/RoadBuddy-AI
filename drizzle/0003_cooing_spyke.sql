ALTER TABLE "users" ALTER COLUMN "conversationState" SET DATA TYPE text;--> statement-breakpoint
ALTER TABLE "users" ALTER COLUMN "conversationState" SET DEFAULT 'UNSPECIFIED'::text;--> statement-breakpoint
DROP TYPE "public"."ConversationState";--> statement-breakpoint
CREATE TYPE "public"."ConversationState" AS ENUM('UNSPECIFIED', 'MAIN_MENU', 'FLOW');--> statement-breakpoint
ALTER TABLE "users" ALTER COLUMN "conversationState" SET DEFAULT 'UNSPECIFIED'::"public"."ConversationState";--> statement-breakpoint
ALTER TABLE "users" ALTER COLUMN "conversationState" SET DATA TYPE "public"."ConversationState" USING "conversationState"::"public"."ConversationState";--> statement-breakpoint
ALTER TABLE "users" ADD COLUMN "chat_id" varchar(15) NOT NULL;