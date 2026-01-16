"""Когнитивный цикл"""
import random
import numpy as np
from typing import Dict, Any, Optional, List
from .emotion_engine import EmotionEngine, EmotionType
from .skill_system import SkillSystem
from .safety_system import SafetySystem, SafetyMode

class CognitiveCycle:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.emotion = EmotionEngine()
        self.skills = SkillSystem()
        self.safety = SafetySystem()
        self.memory = []
        self.cycle_count = 0
        self.client = None
        if api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key)
            except:
                pass
    
    def run_cycle(self, user_input: str) -> str:
        self.cycle_count += 1
        safe, msg = self.safety.check_input(user_input)
        if not safe:
            return f"⚠️ {msg}"
        self._analyze_input(user_input)
        response = self._generate_response(user_input)
        self._update_skills(user_input)
        self.emotion.decay()
        self.memory.append({"input": user_input, "output": response})
        if len(self.memory) > 100:
            self.memory = self.memory[-100:]
        return response
    
    def _analyze_input(self, text: str):
        text_lower = text.lower()
        if any(w in text_lower for w in ["привет", "здравствуй", "добрый"]):
            self.emotion.apply_stimulus(EmotionType.JOY, 0.3)
        elif any(w in text_lower for w in ["грустно", "плохо", "печаль"]):
            self.emotion.apply_stimulus(EmotionType.SADNESS, 0.4)
        elif any(w in text_lower for w in ["злюсь", "бесит", "раздражает"]):
            self.emotion.apply_stimulus(EmotionType.ANGER, 0.3)
        elif "?" in text:
            self.emotion.apply_stimulus(EmotionType.INTEREST, 0.2)
    
    def _generate_response(self, user_input: str) -> str:
        if self.client:
            try:
                emotion, conf = self.emotion.get_dominant_emotion()
                system_prompt = f"Ты AI-компаньон. Твоя эмоция: {emotion.value} ({conf:.0%}). Отвечай кратко и дружелюбно."
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    max_tokens=500
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"Ошибка API: {e}"
        return self._fallback_response(user_input)
    
    def _fallback_response(self, text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ["привет", "здравствуй"]):
            return "Привет! Рад тебя видеть! 😊"
        elif "как дела" in text_lower:
            emotion, _ = self.emotion.get_dominant_emotion()
            return f"У меня всё хорошо! Чувствую {emotion.value}. А у тебя как?"
        elif "?" in text:
            return "Интересный вопрос! Дай подумать..."
        return "Понял тебя! Что-нибудь ещё?"
    
    def _update_skills(self, text: str):
        text_lower = text.lower()
        if any(w in text_lower for w in ["привет", "пока", "спасибо"]):
            self.skills.use_skill("приветствие")
        if any(w in text_lower for w in ["найди", "поищи", "загугли"]):
            self.skills.use_skill("поиск_в_интернете")
        if any(w in text_lower for w in ["грустно", "плохо", "расстроен"]):
            self.skills.use_skill("эмпатия")
    
    def get_state(self) -> Dict[str, Any]:
        emotion, confidence = self.emotion.get_dominant_emotion()
        return {
            "cycle": self.cycle_count,
            "emotion": emotion.value,
            "confidence": confidence,
            "mood": self.emotion.get_mood_description(),
            "pad": {
                "pleasure": self.emotion.pad.pleasure,
                "arousal": self.emotion.pad.arousal,
                "dominance": self.emotion.pad.dominance,
            },
            "total_level": self.skills.get_total_level(),
            "safety_mode": self.safety.mode.value,
        }
