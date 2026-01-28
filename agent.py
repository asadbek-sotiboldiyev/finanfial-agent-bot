import logging
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SYSTEM_INSTRUCTION = """Extract transactions data from given text and return JSON data in this format: [{"amount":300,"description":"ovqatlanish","type":"in|out"}]. Only return list of JSON, don't return anything else"""
MODEL_NAME = str(os.getenv("GEMINI_MODEL_NAME"))

logger = logging.getLogger(__name__)

# instruction
# """Extract data from given text and return JSON data in this format: {"amount":300, "description": "ovqatlanish"}. Only return JSON, don't return anything else"""


class Agent:
    def __init__(self):
        """Bir marta API key bilan yaratiladi"""
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_name = MODEL_NAME
        self.system_instruction = SYSTEM_INSTRUCTION

    def ask(self, message) -> str:
        """Savol berish va javob olish"""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                response_mime_type="application/json",
            ),
        )
        return str(response.text)
