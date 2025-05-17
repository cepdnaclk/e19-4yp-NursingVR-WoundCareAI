import fs from "fs";
import OpenAI from "openai";
import "dotenv/config";
const openai = new OpenAI({
  apiKey: process.env.OPEN_AI_API_KEY,
});

const file = await client.files.create({
  file: fs.createReadStream("draconomicon.pdf"),
  purpose: "user_data",
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
            file_id: file.id,
          },
        },
        {
          type: "text",
          text: "What is the first dragon in the book?",
        },
      ],
    },
  ],
});

console.log(completion.choices[0].message.content);
