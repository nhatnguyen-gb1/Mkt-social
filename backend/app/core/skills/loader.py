import os
import logging
from typing import Optional, Dict, Any
import yaml
from app.core.skills.model import Skill, SkillMetadata

logger = logging.getLogger("aimos.skills.loader")


class SkillLoader:
    """
    SkillLoader parses and validates Skill packages from filesystem directories.
    Reads SKILL.md, RULES.md, EXAMPLES.md, and EVALS.md safely.
    """

    @classmethod
    def load_skill_from_dir(cls, skill_dir: str) -> Skill:
        """
        Loads a single skill from a given directory path.
        """
        if not os.path.exists(skill_dir) or not os.path.isdir(skill_dir):
            return Skill(
                metadata=SkillMetadata(name=os.path.basename(skill_dir)),
                skill_dir=skill_dir,
                is_valid=False,
                validation_error=f"Directory '{skill_dir}' does not exist.",
            )

        skill_md_path = os.path.join(skill_dir, "SKILL.md")
        rules_md_path = os.path.join(skill_dir, "RULES.md")
        examples_md_path = os.path.join(skill_dir, "EXAMPLES.md")
        evals_md_path = os.path.join(skill_dir, "EVALS.md")

        # 1. Validate mandatory SKILL.md
        if not os.path.exists(skill_md_path):
            logger.error(f"[SKILL LOADER ERROR] Mandatory file missing: {skill_md_path}")
            skill_name = os.path.basename(skill_dir)
            return Skill(
                metadata=SkillMetadata(name=skill_name),
                skill_dir=skill_dir,
                is_valid=False,
                validation_error=f"Mandatory file 'SKILL.md' missing in '{skill_dir}'.",
            )

        # 2. Parse SKILL.md metadata (YAML or key-value markdown)
        metadata = cls._parse_skill_md(skill_md_path, os.path.basename(skill_dir))

        # 3. Read optional files with graceful fallback
        rules_content = cls._read_file_safe(rules_md_path)
        examples_content = cls._read_file_safe(examples_md_path)
        evals_content = cls._read_file_safe(evals_md_path)

        return Skill(
            metadata=metadata,
            rules_content=rules_content,
            examples_content=examples_content,
            evals_content=evals_content,
            skill_dir=skill_dir,
            is_valid=True,
        )

    @classmethod
    def _parse_skill_md(cls, file_path: str, fallback_name: str) -> SkillMetadata:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Attempt YAML load
            parsed_data = yaml.safe_load(content)
            if isinstance(parsed_data, dict):
                return SkillMetadata(
                    name=str(parsed_data.get("name") or fallback_name),
                    version=str(parsed_data.get("version") or "1.0.0"),
                    description=str(parsed_data.get("description") or ""),
                    purpose=str(parsed_data.get("purpose") or ""),
                    inputs=parsed_data.get("inputs") or [],
                    outputs=parsed_data.get("outputs") or [],
                    workflow=parsed_data.get("workflow") or [],
                    constraints=parsed_data.get("constraints") or [],
                    dependencies=parsed_data.get("dependencies") or [],
                )
        except Exception as exc:
            logger.warning(f"[SKILL LOADER WARN] Failed to parse YAML in {file_path}: {exc}. Using fallback.")

        return SkillMetadata(name=fallback_name, version="1.0.0")

    @classmethod
    def _read_file_safe(cls, file_path: str) -> str:
        if not os.path.exists(file_path):
            logger.debug(f"[SKILL LOADER] Optional file missing: {file_path}")
            return ""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as exc:
            logger.warning(f"[SKILL LOADER WARN] Error reading {file_path}: {exc}")
            return ""
