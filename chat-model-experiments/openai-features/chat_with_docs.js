import fs from "fs";
import OpenAI from "openai";
import "dotenv/config";
const client = new OpenAI({
  apiKey: process.env.OPEN_AI_API_KEY,
});

const completion = await client.chat.completions.create({
  model: "gpt-4.1",
  messages: [
    {
      role: "user",
      content: [
        {
          type: "file",
          file: {
            file_id: "file-EBvboLPZgLs2EE3i1agkj6",
          },
        },
        {
          type: "text",
          text: "what is software engineering?",
        },
      ],
    },
  ],
  max_tokens: 1000,
});

console.log(completion.choices[0].message.content);
