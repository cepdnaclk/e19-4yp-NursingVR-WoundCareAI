
from agents import Agent
from agents import Runner

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",

)

math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",

)

triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[history_tutor_agent, math_tutor_agent],

)

async def main():
    print('hello')
    result = await Runner.run(triage_agent, "What is the capital of France?")
    print(result.final_output)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())