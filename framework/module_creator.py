from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional, Tuple

import questionary

from framework.framework_commons.yaml_util import YamlFile
from .utils import (
    get_user_input,
    get_user_path,
    initialize_git_repo,
    repo_cloner,
)


class ModuleCreator:
    """Handle module creation workflows for the ADHD Framework CLI."""

    DEFAULT_MODULE_TYPES: List[Tuple[str, str]] = [
        ("manager", "For coordination of external or project-wide systems"),
        ("plugin", "For implementing specific functionality"),
        ("util", "For concise utility functions and helpers enhancing framework capabilities"),
        ("mcp", "For Model Context Protocol server implementations"),
    ]

    def __init__(
        self,
        framework_dir: Path,
        module_template_url: str,
        module_types: Optional[List[Tuple[str, str]]] = None,
    ) -> None:
        self.framework_dir = framework_dir
        self.module_template_url = module_template_url
        self.module_types = module_types or self.DEFAULT_MODULE_TYPES

    def create_module(
        self,
        module_name: Optional[str] = None,
        module_location: Optional[str] = None,
        module_type: Optional[str] = None,
    ) -> bool:
        """Create a module using the stored configuration and helper callbacks."""
        if not module_name:
            module_name = get_user_input(
                "Enter module name (please use snake_case):",
                "new_adhd_module",
            )

        if module_name:
            normalized = self._normalize_module_name(module_name)
            if normalized != module_name:
                print(
                    f"⚠️ Module name '{module_name}' is not in snake_case format. "
                    f"✅ Will use '{normalized}' instead."
                )
                module_name = normalized

        if not module_name:
            print("✗ Module name cannot be empty!")
            return False

        if not module_location:
            module_location = get_user_path("Enter module location:")

        if not module_location:
            module_location = str(Path.cwd())

        if not module_type:
            module_type = self._get_module_type()
            if not module_type:
                return False

        module_path = Path(module_location) / module_name
        module_path.parent.mkdir(parents=True, exist_ok=True)

        if module_path.exists():
            print(f"✗ Directory {module_path} already exists!")
            return False

        print(f"\nYour new module will be named '{module_name}'")
        print(f"\nCreating module '{module_name}' at {module_path}")

        if not repo_cloner.clone(str(module_path), self.module_template_url):
            return False

        if not self._create_module_init_yaml(module_path, module_name, module_type):
            return False

        self._add_generated_files_to_new_module(module_name, module_path)
        self._add_generated_files_to_specific_module_type(
            module_name,
            module_path,
            module_type,
        )

        print(f"\n🎉 Module '{module_name}' created successfully!")
        print(f"Location: {module_path}")
        print(f"Type: {module_type}")
        print(f"Folder path: {module_type}/{module_name}")

        self._prompt_git_initialization(module_path)
        return True

    def _get_module_type(self) -> Optional[str]:
        choices = [f"{module_type} - {description}" for module_type, description in self.module_types]
        default_choice = choices[0] if choices else None

        selected = questionary.select(
            "Choose module type:",
            choices=choices,
            default=default_choice,
        ).ask()

        if not selected:
            return None

        return selected.split(" - ")[0]

    def _create_module_init_yaml(
        self,
        module_path: Path,
        module_name: str,
        module_type: str,
    ) -> bool:
        folder_path = f"{module_type}s/{module_name}"
        init_content = {
            "version": "0.0.1",
            "folder_path": folder_path,
            "type": module_type,
            "requirements": [],
        }

        init_file = module_path / "init.yaml"
        yaml_file = YamlFile(init_content)
        if yaml_file.save(init_file):
            print("✓ Created init.yaml with module configuration")
            return True

        print("✗ Failed to create init.yaml")
        return False

    def _replace_placeholders(self, content: str, module_name: str) -> str:
        replacements = {
            "{{module_name}}": module_name,
            "{{ModuleNameToCamelCase}}": self._to_camel_case(module_name),
        }
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        return content

    def _add_generated_files_to_new_module(self, module_name: str, module_path: Path) -> None:
        template_dir = self.framework_dir / "module_additional_files"
        if not template_dir.exists():
            print("⚠️  Template files are missing; skipping extra file generation.")
            return

        self._add_generated_files_from_directory(template_dir, module_name, module_path)

    def _add_generated_files_to_specific_module_type(self, module_name: str, module_path: Path, module_type: str) -> None:
        template_dir = self.framework_dir / "module_additional_files" / module_type

        if not template_dir.exists():
            return

        self._add_generated_files_from_directory(template_dir, module_name, module_path)

    def _add_generated_files_from_directory(
        self,
        template_dir: Path,
        module_name: str,
        module_path: Path,
    ) -> None:
        for template_file in sorted(template_dir.iterdir()):
            if template_file.is_dir():
                continue

            try:
                content = template_file.read_text(encoding="utf-8")
                content = self._replace_placeholders(content, module_name)

                output_name = self._replace_placeholders(template_file.name, module_name)

                exception_txt = ["requirements.txt"]

                if output_name.endswith(".txt") and output_name not in exception_txt:
                    output_name = output_name[:-4]

                destination = module_path / output_name
                action = "Replaced" if destination.exists() else "Added"
                destination.write_text(content, encoding="utf-8")
                print(f"✓ {action} {output_name}")
            except Exception as error:
                print(f"⚠️  Failed to add {template_file.name}: {error}")

    def _prompt_git_initialization(self, module_path: Path) -> None:
        try:
            remote_url = questionary.text(
                "Enter GitHub repository URL (leave blank to skip git init/push):",
                default="",
            ).ask()
            if remote_url:
                initialize_git_repo(module_path, remote_url.strip())
            else:
                print("(Skipping git setup – no URL provided)")
        except Exception as error:
            print(f"⚠️  Skipped git initialization: {error}")

    @staticmethod
    def _normalize_module_name(name: str) -> str:
        transformed = name.replace("-", " ").replace(".", " ")
        transformed = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", transformed)
        transformed = re.sub(r"([a-z\d])([A-Z])", r"\1 \2", transformed)
        snake = "_".join(transformed.split()).lower()
        return snake

    @staticmethod
    def _to_camel_case(name: str) -> str:
        parts = name.replace("-", "_").replace(".", "_").split("_")
        return "".join(part.capitalize() for part in parts if part)