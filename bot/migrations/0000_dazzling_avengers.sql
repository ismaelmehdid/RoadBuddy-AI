CREATE TYPE "public"."ConversationState" AS ENUM('MAIN_MENU', 'FLOW');--> statement-breakpoint
CREATE TYPE "public"."userCity" AS ENUM('Paris', 'ERROR');--> statement-breakpoint
CREATE TYPE "public"."userCountry" AS ENUM('FRANCE', 'ERROR');--> statement-breakpoint
CREATE TABLE "users" (
	"id" integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY (sequence name "users_id_seq" INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START WITH 1 CACHE 1),
	"chat_id" integer NOT NULL,
	"conversationState" "ConversationState" DEFAULT 'MAIN_MENU',
	"wrong_answer_count" integer DEFAULT 0,
	"correct_answer_count" integer DEFAULT 0,
	"current_correct_answer_id" varchar(1) DEFAULT '',
	"city" "userCity",
	"country" "userCountry"
);
