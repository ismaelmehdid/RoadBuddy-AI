ALTER TABLE "users" ALTER COLUMN "city" SET DATA TYPE text;--> statement-breakpoint
DROP TYPE "public"."userCity";--> statement-breakpoint
CREATE TYPE "public"."userCity" AS ENUM('Paris', 'ERROR');--> statement-breakpoint
ALTER TABLE "users" ALTER COLUMN "city" SET DATA TYPE "public"."userCity" USING "city"::"public"."userCity";