import OpenAI from "openai";
import readline from "readline";
import "dotenv/config";

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const messages = [];

while (true) {
  // Wait for user input
  const input = await new Promise((resolve) => {
    rl.question("Enter your message: ", resolve);
  });

  if (input === "exit") {
    rl.close();
    break;
  }

  messages.push({ role: "user", content: input });

  try {
    const response = await openai.chat.completions.create({
      messages: messages,
      model: "o4-mini",
      store: true,
    });

    console.log("AI:", response.choices[0].message.content);
    messages.push({
      role: "assistant",
      content: response.choices[0].message.content,
    });
  } catch (error) {
    console.error("Error:", error.message);
  }

  console.log("waiting for response...");
}
