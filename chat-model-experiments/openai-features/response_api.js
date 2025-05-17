import OpenAI from "openai";
import "dotenv/config";

// using openAI response API to manege conversation.
//  just send the previous response id. for each request. it will remember the context.
//  But charges are applied in same way as chat completion API. (using messages array)

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const response = await openai.responses.create({
  model: "gpt-4o-mini",
  input: "i have 5 pets",
  store: true,
});

console.log(response.output_text);

const secondResponse = await openai.responses.create({
  model: "gpt-4o-mini",
  previous_response_id: response.id,
  input: [{ role: "user", content: "They are very funny." }],
  store: true,
});

console.log(secondResponse.output_text);

const thirdResponse = await openai.responses.create({
  model: "gpt-4o-mini",
  previous_response_id: secondResponse.id,
  input: [{ role: "user", content: "How many pets do i have?" }],
  store: true,
});

console.log(thirdResponse.output_text);
