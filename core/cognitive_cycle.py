"""Когнитивный цикл"""

from typing import Dict, Any
from .emotion_engine import EmotionEngine, EmotionType
from .skill_system import SkillSystem
from .safety_system import SafetySystem


class CognitiveCycle:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.emotion = EmotionEngine()
        self.skills = SkillSystem()
        self.safety = SafetySystem()

        # Эпизодическая память (как было)
        self.memory = []
        # Рабочая память короткого контекста
        self.working_memory = []

        self.cycle_count = 0
        self.client = None

        if api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key)
            except Exception:
                pass

    # ================== Публичный вход ==================

    def run_cycle(self, user_input: str) -> str:
        """Полный когнитивный цикл из 10 шагов."""

        self.cycle_count += 1

        # 1. Perception — парсинг входа + безопасность
        safe, msg = self._perceive(user_input)
        if not safe:
            return f"⚠️ {msg}"

        # 2. Working Memory Update — добавление перцептов
        self._update_working_memory(user_input)

        # 3. Attention — выбор фокуса
        context = self._apply_attention()

        # 4. Retrieval — получение релевантных воспоминаний
        retrieved = self._retrieve_memory(user_input)

        # 5. Emotion Update — обновление эмоций
        self._update_emotion(user_input)

        # 6. Goal Check — мониторинг целей (заглушка)
        self._check_goals(user_input, context, retrieved)

        # 7. Action Selection — выбор действия / rule engine
        action = self._select_action(user_input, context, retrieved)

        # 8. Action Execution — генерация ответа
        response = self._execute_action(user_input, action, context, retrieved)

        # 9. Learning — сохранение эпизода
        self._learn(user_input, response, context, retrieved)

        # 10. Cleanup — decay эмоций и памяти
        self._cleanup()

        return response

    # ================== 1. Perception ==================

    def _perceive(self, user_input: str):
        """
        Perception: здесь можно расширять парсинг, intent, слоты.
        Пока — проверка безопасности, как было в run_cycle.
        """
        safe, msg = self.safety.check_input(user_input)
        return safe, msg

    # ================== 2. Working Memory Update ==================

    def _update_working_memory(self, user_input: str):
        """
        Добавляем текущий ввод в рабочую память.
        """
        self.working_memory.append({"role": "user", "content": user_input})
        # Ограничение размера рабочей памяти
        if len(self.working_memory) > 20:
            self.working_memory = self.working_memory[-20:]

    # ================== 3. Attention ==================

    def _apply_attention(self):
        """
        Attention: выделение фокуса из рабочей памяти.
        Сейчас — просто последние N сообщений.
        """
        focus_window = 10
        return self.working_memory[-focus_window:]

    # ================== 4. Retrieval ==================

    def _retrieve_memory(self, user_input: str):
        """
        Retrieval: получение релевантных прошлых эпизодов.
        Пока — просто последние несколько элементов self.memory.
        """
        retrieved_window = 5
        return self.memory[-retrieved_window:]

    # ================== 5. Emotion Update ==================

    def _update_emotion(self, text: str):
        """
        Emotion Update: то, что раньше было _analyze_input.
        """
        text_lower = text.lower()

        if any(w in text_lower for w in ["привет", "здравствуй", "добрый"]):
            self.emotion.apply_stimulus(EmotionEngine.EmotionType.JOY, 0.3)  # type: ignore
        elif any(w in text_lower for w in ["грустно", "плохо", "печаль"]):
            self.emotion.apply_stimulus(EmotionEngine.EmotionType.SADNESS, 0.4)  # type: ignore
        elif any(w in text_lower for w in ["злюсь", "бесит", "раздражает"]):
            self.emotion.apply_stimulus(EmotionEngine.EmotionType.ANGER, 0.3)  # type: ignore
        elif "?" in text:
            self.emotion.apply_stimulus(EmotionEngine.EmotionType.INTEREST, 0.2)  # type: ignore

    # Если хочешь без type: ignore — используй импорт EmotionType, как было:
    # self.emotion.apply_stimulus(EmotionType.JOY, 0.3) и т.д.

    # ================== 6. Goal Check ==================

    def _check_goals(self, user_input: str, context, retrieved):
        """
        Goal Check: мониторинг прогресса целей.
        Пока заглушка, чтобы не ломать текущую архитектуру.
        """
        return

    # ================== 7. Action Selection ==================

    def _select_action(self, user_input: str, context, retrieved) -> str:
        """
        Action Selection: выбор, что делать.
        Здесь можно вешать правила, команды и выбор LLM / fallback.
        """
        text_lower = user_input.lower()

        # простые команды
        if text_lower.startswith("/status"):
            return "status"
        if text_lower.startswith("/reset"):
            return "reset"

        # если есть клиент LLM — используем его, иначе fallback
        if self.client:
            return "llm"
        return "fallback"

    # ================== 8. Action Execution ==================

    def _execute_action(self, user_input: str, action: str, context, retrieved) -> str:
        """
        Action Execution: выполняем выбранное действие.
        """

        # спец-действия
        if action == "status":
            state = self.get_state()
            return (
                f"Цикл: {state['cycle']}, эмоция: {state['emotion']} "
                f"({state['confidence']:.0%}), настроение: {state['mood']}"
            )

        if action == "reset":
            self.working_memory.clear()
            self.memory.clear()
            return "Память очищена. Начинаем заново!"

        # обновляем навыки (как раньше _update_skills)
        self._update_skills(user_input)

        # llm / fallback
        if action == "llm":
            return self._generate_llm_response(user_input, context, retrieved)

        return self._fallback_response(user_input)

    def _generate_llm_response(self, user_input: str, context, retrieved) -> str:
        """
        Генерация ответа через LLM (как старый _generate_response, но с контекстом).
        """
        if not self.client:
            return self._fallback_response(user_input)

        try:
            emotion, conf = self.emotion.get_dominant_emotion()
            system_prompt = (
                f"Ты AI-компаньон. Твоя эмоция: {emotion.value} ({conf:.0%}). "
                f"Отвечай кратко и дружелюбно."
            )

            messages = [{"role": "system", "content": system_prompt}]

            # подмешиваем контекст внимания (по желанию можно убрать)
            for m in context:
                messages.append({"role": m["role"], "content": m["content"]})

            messages.append({"role": "user", "content": user_input})

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=500,
            )
            return response.choices[0].message.content

        except Exception as e:
            return f"Ошибка API: {e}"

    # ================== Fallback ==================

    def _fallback_response(self, text: str) -> str:
        """
        Старый fallback-ответ, оставлен без изменений.
        """
        text_lower = text.lower()

        if any(w in text_lower for w in ["привет", "здравствуй"]):
            return "Привет! Рад тебя видеть! 😊"
        elif "как дела" in text_lower:
            emotion, _ = self.emotion.get_dominant_emotion()
            return f"У меня всё хорошо! Чувствую {emotion.value}. А у тебя как?"
        elif "?" in text:
            return "Интересный вопрос! Дай подумать..."
        return "Понял тебя! Что-нибудь ещё?"

    # ================== Skills ==================

    def _update_skills(self, text: str):
        """
        Логика прокачки навыков из старой версии.
        """
        text_lower = text.lower()

        if any(w in text_lower for w in ["привет", "пока", "спасибо"]):
            self.skills.use_skill("приветствие")
        if any(w in text_lower for w in ["найди", "поищи", "загугли"]):
            self.skills.use_skill("поиск_в_интернете")
        if any(w in text_lower for w in ["грустно", "плохо", "расстроен"]):
            self.skills.use_skill("эмпатия")

    # ================== 9. Learning ==================

    def _learn(self, user_input: str, response: str, context, retrieved):
        """
        Learning: сохраняем эпизод в память.
        Раньше сохранялось только input/output; теперь добавлен контекст.
        """
        episode = {
            "input": user_input,
            "output": response,
            "context": context,
            "retrieved": retrieved,
        }
        self.memory.append(episode)

        if len(self.memory) > 100:
            self.memory = self.memory[-100:]

    # ================== 10. Cleanup ==================

    def _cleanup(self):
        """
        Cleanup: decay эмоций и потенциальный decay других состояний.
        """
        self.emotion.decay()

    # ================== Состояние ==================

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

