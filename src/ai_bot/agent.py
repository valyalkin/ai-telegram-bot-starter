import asyncio
import uuid

from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

checkpointer = InMemorySaver()

agent = create_react_agent(
    model="openai:gpt-5-nano",
    tools=[],
    prompt="""
    You are a helpful assistant. 
    Answer the question in the format which would fit telegram message format, do not return markdown.
    """,
    checkpointer=checkpointer
)


if __name__ == '__main__':
    # Run the agent
    response = agent.invoke(
        input={"messages": [{"role": "user", "content": "How is it going?"}]},
        config={"configurable": {"thread_id": str(uuid.uuid4())}}
    )

    print(response['messages'][-1].content)

