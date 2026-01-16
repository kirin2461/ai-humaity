"""Система навыков с прокачкой"""
from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum
import math

class SkillLevel(Enum):
    NOVICE = "Новичок"
    BEGINNER = "Начинающий"
    INTERMEDIATE = "Средний"
    ADVANCED = "Продвинутый"
    EXPERT = "Эксперт"

@dataclass
class Skill:
    name: str
    category: str
    experience: float = 0.0
    level: SkillLevel = SkillLevel.NOVICE
    uses: int = 0
    tags: List[str] = field(default_factory=list)

class SkillSystem:
    XP_THRESHOLDS = {
        SkillLevel.NOVICE: 0,
        SkillLevel.BEGINNER: 100,
        SkillLevel.INTERMEDIATE: 500,
        SkillLevel.ADVANCED: 2000,
        SkillLevel.EXPERT: 10000,
    }
    
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self.total_experience = 0.0
        self._init_default_skills()
    
    def _init_default_skills(self):
        defaults = [
            ("приветствие", "общение", ["social"]),
            ("поиск_в_интернете", "технические", ["web", "research"]),
            ("эмпатия", "общение", ["emotional"]),
            ("анализ", "технические", ["logic"]),
            ("креативность", "творческие", ["creative"]),
        ]
        for name, cat, tags in defaults:
            self.skills[name] = Skill(name=name, category=cat, tags=tags)
    
    def use_skill(self, name: str, success: bool = True) -> float:
        if name not in self.skills:
            self.skills[name] = Skill(name=name, category="общение")
        skill = self.skills[name]
        base_xp = 10 if success else 3
        bonus = 1.0 + (skill.uses * 0.01)
        xp = base_xp * min(bonus, 2.0)
        skill.experience += xp
        skill.uses += 1
        self.total_experience += xp
        self._update_level(skill)
        return xp
    
    def _update_level(self, skill: Skill):
        for level in reversed(list(SkillLevel)):
            if skill.experience >= self.XP_THRESHOLDS[level]:
                skill.level = level
                break
    
    def get_skill(self, name: str) -> Skill:
        return self.skills.get(name)
    
    def get_total_level(self) -> int:
        return int(math.log10(self.total_experience + 1) * 2) + 1
    
    def get_skills_by_category(self, category: str) -> List[Skill]:
        return [s for s in self.skills.values() if s.category == category]
