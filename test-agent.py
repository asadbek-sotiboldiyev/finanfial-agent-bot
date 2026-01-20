import os

from dotenv import load_dotenv

from agent import Agent

load_dotenv()

key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL")
agent = Agent(
    api_key=key,
    model_name=model,
    system_instruction="""Extract data from given text and return JSON data in this format: {"amount":300, "description": "ovqatlanish"}. Only return JSON, don't return anything else"""
)
response = agent.ask(
    "bugun o'qishga avtobusda borib keldim. avtobus 1700 turadi. 30000 ovqatlandim. 150000 yangi naushnik oldim"
)
print(response)
