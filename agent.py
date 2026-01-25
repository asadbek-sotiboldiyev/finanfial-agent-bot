import logging
import os

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# instruction
# """Extract data from given text and return JSON data in this format: {"amount":300, "description": "ovqatlanish"}. Only return JSON, don't return anything else"""


class Agent:
    def __init__(self, api_key, model_name):
        """Bir marta API key bilan yaratiladi"""
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.system_instruction = """Extract data from given text and return JSON data in this format: {"amount":300, "description": "ovqatlanish", "type":"in|out"}. Only return JSON, don't return anything else"""

    def ask(self, message):
        """Savol berish va javob olish"""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                response_mime_type="application/json",
            ),
        )
        return response.text
