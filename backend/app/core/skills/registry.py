import os
import logging
from typing import Dict, List, Optional
from app.core.skills.model import Skill
from app.core.skills.loader import SkillLoader

logger = logging.getLogger("aimos.skills.registry")


class SkillRegistry:
    """
    Central SkillRegistry for discovering, registering, and retrieving AIMOS Skills.
    """

    def __init__(self):
        self._skills: Dict[str, Skill] = {}

    def discover_skills(self, root_dir: str):
        """
        Scans root_dir for skill subdirectories and registers valid skills.
        """
        if not os.path.exists(root_dir) or not os.path.isdir(root_dir):
            logger.warning(f"[SKILL REGISTRY WARN] Root dir '{root_dir}' does not exist.")
            return

        logger.info(f"[SKILL REGISTRY] Discovering skills in '{root_dir}'...")
        count = 0
        for entry in os.listdir(root_dir):
            full_path = os.path.join(root_dir, entry)
            if os.path.isdir(full_path):
                skill = SkillLoader.load_skill_from_dir(full_path)
                if skill.is_valid:
                    self.register_skill(skill)
                    count += 1
                else:
                    logger.warning(
                        f"[SKILL REGISTRY] Skipped invalid skill in '{full_path}': {skill.validation_error}"
                    )
        logger.info(f"[SKILL REGISTRY] Total valid skills loaded: {count}")

    def register_skill(self, skill: Skill):
        """
        Registers a skill object.
        """
        skill_name = skill.metadata.name
        self._skills[skill_name] = skill
        logger.info(f"[SKILL REGISTRY] Registered skill '{skill_name}' (v{skill.metadata.version})")

    def get_skill(self, skill_name: str) -> Optional[Skill]:
        return self._skills.get(skill_name)

    def list_skills(self) -> List[Skill]:
        return list(self._skills.values())

    def has_skill(self, skill_name: str) -> bool:
        return skill_name in self._skills

    def get_skill_version(self, skill_name: str) -> Optional[str]:
        skill = self.get_skill(skill_name)
        return skill.metadata.version if skill else None


# Global Singleton Instance
skill_registry = SkillRegistry()

# Default discovery on backend/skills
default_skills_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "skills")
)
if os.path.exists(default_skills_path):
    skill_registry.discover_skills(default_skills_path)
