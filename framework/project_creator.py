from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import questionary

from framework.framework_commons.yaml_util import YamlUtil
from .utils import (
    clone_template,
    get_user_input,
    get_user_path,
    initialize_git_repo,
)


@dataclass
class ADHDFrameworkTemplateSet:
    """Representation of a template set discovered on disk."""

    folder_path: Path
    folder: str = ""
    name: str = ""
    modules: Optional[List[str]] = None
    template_repo: str = ""
    description: str = ""

    def __post_init__(self) -> None:
        self.folder = self.folder_path.name
        init_file = self.folder_path / "init.yaml"
        if not init_file.exists():
            raise FileNotFoundError(f"init.yaml not found in {self.folder_path}")

        yaml_file = YamlUtil.read_yaml(init_file)
        if not yaml_file:
            raise ValueError(f"Invalid init.yaml format in {self.folder}")

        if not self.name:
            self.name = yaml_file.get("name", self.folder)
        if self.modules is None:
            self.modules = yaml_file.get("modules", [])
        self.description = yaml_file.get("description", "No description")
        self.template_repo = yaml_file.get("template_repo", "")


class ProjectCreator:
    """Handle project creation workflows for the ADHD Framework CLI."""

    def __init__(
        self,
        template_sets_dir: Path,
        template_url: str,
    ) -> None:
        self.template_sets_dir = template_sets_dir
        self.template_url = template_url

    def list_template_sets(self) -> List[dict]:
        """Discover available template sets from the template directory."""
        if not self.template_sets_dir.exists():
            print("No template sets found!")
            return []

        templates: List[dict] = []
        for folder_path in self.template_sets_dir.iterdir():
            if folder_path.is_dir():
                try:
                    template_set = ADHDFrameworkTemplateSet(folder_path=folder_path)
                    templates.append(
                        {
                            "folder": template_set.folder,
                            "name": template_set.name,
                            "description": template_set.description,
                            "template_repo": template_set.template_repo,
                        }
                    )
                except Exception as error:
                    print(
                        f"Warning: Could not load template set {folder_path.name}: {error}"
                    )
        return templates

    def choose_template_set(self) -> Optional[str]:
        """Interactively choose a template set using questionary."""
        templates = self.list_template_sets()
        if not templates:
            return None

        choices: List[str] = []
        default_template: Optional[str] = None
        for template in templates:
            choice_text = f"{template['name']} - {template['description']}"
            choices.append(choice_text)
            if template["folder"] == "default":
                default_template = choice_text

        if not default_template and choices:
            default_template = choices[0]

        selected = questionary.select(
            "Choose template set:",
            choices=choices,
            default=default_template,
        ).ask()

        if not selected:
            return None

        for template in templates:
            if f"{template['name']} - {template['description']}" == selected:
                return template["folder"]
        return None

    def validate_template_set(self, template_set_name: str) -> bool:
        """Confirm that the provided template set exists."""
        templates = self.list_template_sets()
        for template in templates:
            if template["folder"] == template_set_name:
                return True

        available = [template["folder"] for template in templates]
        print(f"✗ Template set '{template_set_name}' not found!")
        if available:
            print(f"Available template sets: {', '.join(available)}")
        return False

    def replace_init_yaml(self, project_path: str, template_set_folder: str) -> bool:
        """Overwrite project init.yaml with the selected template set configuration."""
        template_file = self.template_sets_dir / template_set_folder / "init.yaml"
        init_file = Path(project_path) / "init.yaml"

        if not template_file.exists():
            print(f"✗ Template file not found: {template_file}")
            return False

        try:
            yaml_file = YamlUtil.read_yaml(template_file)
            yaml_file.set("template_repo", self.template_url)
            if yaml_file.save(init_file):
                print(
                    f"✓ Replaced init.yaml with {template_set_folder}/init.yaml"
                )
                return True
            print(f"✗ Failed to save init.yaml to {init_file}")
            return False
        except Exception as error:
            print(f"✗ Failed to replace init.yaml: {error}")
            return False

    def get_template_repo_for_set(self, template_set_folder: str) -> str:
        """Resolve the template repository URL for the chosen set."""
        template_file = self.template_sets_dir / template_set_folder / "init.yaml"
        if not template_file.exists():
            return self.template_url

        yaml_file = YamlUtil.read_yaml(template_file)
        if not yaml_file:
            print("Warning: Could not read template set config, using default template")
            return self.template_url

        template_repo = yaml_file.get("template_repo", "")
        return template_repo.strip() if template_repo and template_repo.strip() else self.template_url

    def create_project(
        self,
        project_name: Optional[str] = None,
        project_location: Optional[str] = None,
        template_set_name: Optional[str] = None,
    ) -> bool:
        """Create a project using the stored configuration and helper callbacks."""
        if not project_name:
            project_name = get_user_input("Enter project name:", "new-adhd-project")

        if not project_name:
            print("✗ Project name cannot be empty!")
            return False

        if not project_location:
            project_location = get_user_path("Enter project location:")

        if not project_location:
            project_location = str(Path.cwd())

        project_path = Path(project_location) / project_name
        project_path.parent.mkdir(parents=True, exist_ok=True)

        if project_path.exists():
            print(f"✗ Directory {project_path} already exists!")
            return False

        if template_set_name:
            if not self.validate_template_set(template_set_name):
                return False
            template_set = template_set_name
        else:
            template_set = self.choose_template_set()
            if not template_set:
                return False

        print(f"\nCreating project '{project_name}' at {project_path}")

        template_repo_url = self.get_template_repo_for_set(template_set)
        print(f"Using template repository: {template_repo_url}")

        if not clone_template(str(project_path), template_repo_url):
            return False

        if not self.replace_init_yaml(str(project_path), template_set):
            return False

        if not self._run_project_init(str(project_path)):
            return False

        print(f"\n🎉 Project '{project_name}' created successfully!")
        print(f"Location: {project_path}")

        self._prompt_git_initialization(project_path)
        return True

    def _run_project_init(self, project_path: str) -> bool:
        """Execute the generated project's CLI to finish initialization."""
        cli_script = Path(project_path) / "adhd_cli.py"

        if not cli_script.exists():
            print(f"✗ adhd_cli.py not found in {project_path}")
            return False

        print("Running project initialization via ADHD CLI...")
        try:
            subprocess.run([sys.executable, str(cli_script), "init"], cwd=project_path, check=True)
            print("✓ Project initialized successfully!")
            return True
        except subprocess.CalledProcessError as error:
            print(f"✗ Project initialization failed: {error}")
            return False

    def _prompt_git_initialization(self, project_path: Path) -> None:
        """Offer optional git initialization for the newly created project."""
        try:
            remote_url = questionary.text(
                "Enter GitHub repository URL (leave blank to skip git init/push):",
                default="",
            ).ask()
            if remote_url:
                initialize_git_repo(project_path, remote_url.strip())
            else:
                print("(Skipping git setup – no URL provided)")
        except Exception as error:
            print(f"⚠️  Skipped git initialization: {error}")
