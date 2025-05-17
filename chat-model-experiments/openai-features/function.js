import { OpenAI } from "openai";
import "dotenv/config";

//  functions are used to give model access to external APIs, or other function's capabilities to work.

console.log("Function calling example", process.env.OPENAI_API_KEY);

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

async function getWeather(latitude, longitude) {
  const response = await fetch(
    `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m`
  );
  const data = await response.json();
  return data.current.temperature_2m;
}

const tools = [
  {
    type: "function",
    function: {
      name: "get_weather",
      description:
        "Get current temperature for provided coordinates in celsius.",
      parameters: {
        type: "object",
        properties: {
          latitude: { type: "number" },
          longitude: { type: "number" },
        },
        required: ["latitude", "longitude"],
        additionalProperties: false,
      },
      strict: true,
    },
  },
];

const messages = [
  {
    role: "user",
    content: "What's the weather like in Paris today?",
  },
];

const completion = await openai.chat.completions.create({
  model: "gpt-4.1",
  messages: messages,
  tools,
  store: true,
});

console.log(completion.choices[0].message);

const toolCall = completion.choices[0].message.tool_calls[0];
const args = JSON.parse(toolCall.function.arguments);

const result = await getWeather(args.latitude, args.longitude);

console.log(result);

messages.push(completion.choices[0].message);
messages.push({
  role: "tool",
  tool_call_id: toolCall.id,
  content: result.toString(),
});

console.log(messages);

const completion2 = await openai.chat.completions.create({
  model: "gpt-4.1",
  messages,
  tools,
  store: true,
});

console.log(completion2.choices[0].message.content);
