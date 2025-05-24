import { err, ok } from "neverthrow";
import { Result } from "neverthrow";
import { City, Question, QuestionSchema } from "../types/types";

export async function getQuestionImageUrl(city: City): Promise<Result<string, Error>> {

  const url = "https://rdhfgzwwvi.execute-api.eu-central-1.amazonaws.com";
  const response = await fetch(`${url}/api/v1/street-image`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      city: city,
    }),
  });
  if (!response.ok) {
    return err(new Error("Failed to get question image url"));
  }
  const data = await response.json();
  return ok(data.image_url);
}

export async function getQuestion(image_url: string, city: City): Promise<Result<Question, Error>> {
  const url = "https://rdhfgzwwvi.execute-api.eu-central-1.amazonaws.com";
  const response = await fetch(`${url}/api/v1/exam-chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      image_url: image_url,
      city: "Paris", //TODO: Use city from user
    }),
  });
  if (!response.ok) {
    return err(new Error("Failed to get question"));
  }
  const data = await response.json();
  console.log("data", data);
  const question = QuestionSchema.safeParse(data);
  if (!question.success) {
    console.log("question", question);
    return err(new Error("Failed to parse question"));
  }
  return ok(question.data);
}
