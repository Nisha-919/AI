from __future__ import annotations

from typing import Any

import httpx

from config.settings import GROQ_API_KEY, GROQ_API_URL, GROQ_MODEL
from core.database import Database

AUTH_SCHEME = "Bearer"


class GroqAIEngine:
    def __init__(self, database: Database) -> None:
        self.database = database
        self.system_prompt = (
            "You are KAVI Lite, a helpful futuristic desktop assistant. "
            "Reply concisely in friendly Hinglish when appropriate."
        )

    async def generate_response(self, user_text: str) -> str:
        if not GROQ_API_KEY:
            return "GROQ API key missing. Please set GROQ_API_KEY in your environment."

        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.database.fetch_recent())
        messages.append({"role": "user", "content": user_text})

        payload: dict[str, Any] = {
            "model": GROQ_MODEL,
            "messages": messages,
            "temperature": 0.6,
            "max_tokens": 512,
        }

        headers = {"Authorization": f"{AUTH_SCHEME} {GROQ_API_KEY}"}

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(GROQ_API_URL, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError:
            return "Network issue while contacting GROQ. Please try again."
        except (KeyError, IndexError, ValueError):
            return "Unexpected GROQ response. Please retry."

        reply = data["choices"][0]["message"]["content"].strip()
        self.database.add_message("user", user_text)
        self.database.add_message("assistant", reply)
        return reply
