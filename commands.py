from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(slots=True)
class IntentResult:
    intent: str
    confidence: float
    entities: Dict[str, str]


class CommandBrain:
    def __init__(self, min_confidence: float = 0.18) -> None:
        self.min_confidence = min_confidence
        self.intent_map: Dict[str, List[str]] = {
            "open_app": ["open", "launch", "khol", "kholo", "start"],
            "open_website": ["website", "site", "browser", "open"],
            "youtube_search": ["youtube", "video", "play on youtube"],
            "google_search": ["google", "search", "find"],
            "play_music": ["music", "song", "gana", "spotify", "play"],
            "screenshot": ["screenshot", "capture screen", "screen shot"],
            "screen_summary": ["screen", "summarize", "kya likha", "explain code", "pdf summarize"],
            "set_voice_male": ["male voice", "guy voice", "male mode"],
            "set_voice_female": ["female voice", "girl voice", "female mode"],
            "set_theme_dark": ["dark mode", "dark theme"],
            "set_theme_light": ["light mode", "light theme"],
            "help": ["help", "what can you do", "capabilities"],
            "exit": ["quit", "exit", "close aria", "stop listening", "bye"],
        }

    @staticmethod
    def detect_language(text: str) -> str:
        if any("\u0900" <= char <= "\u097f" for char in text):
            return "hi"
        lowered = text.lower()
        hinglish_markers = ["karo", "kholo", "batao", "mujhe", "chalao"]
        if any(marker in lowered for marker in hinglish_markers):
            return "hinglish"
        return "en"

    def _score(self, query: str, keywords: List[str]) -> float:
        q = query.lower()
        if not q:
            return 0.0
        matches = sum(1 for keyword in keywords if keyword in q)
        token_bonus = 0.1 if len(q.split()) > 2 else 0.0
        return min(1.0, (matches / max(1, len(keywords))) + token_bonus)

    def classify(self, query: str) -> IntentResult:
        scored: List[Tuple[str, float]] = [
            (intent, self._score(query, keywords)) for intent, keywords in self.intent_map.items()
        ]
        best_intent, confidence = max(scored, key=lambda item: item[1], default=("unknown", 0.0))
        entities = self._extract_entities(query, best_intent)
        return IntentResult(
            intent=best_intent if confidence > self.min_confidence else "unknown",
            confidence=confidence,
            entities=entities,
        )

    @staticmethod
    def _extract_entities(query: str, intent: str) -> Dict[str, str]:
        lowered = query.lower()
        entities: Dict[str, str] = {}
        if intent == "open_app":
            clean = lowered.replace("open", "").replace("launch", "").replace("kholo", "").replace("khol", "")
            entities["app_name"] = clean.strip() or lowered
        elif intent in {"youtube_search", "google_search"}:
            cleaned = lowered.replace("search", "").replace("youtube", "").replace("google", "").replace("play", "")
            entities["query"] = cleaned.strip()
        elif intent == "open_website":
            entities["url_or_name"] = lowered.replace("open", "").replace("website", "").strip()
        return entities
