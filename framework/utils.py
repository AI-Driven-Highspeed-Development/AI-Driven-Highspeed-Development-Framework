"""Utility helpers shared across the ADHD Framework CLI components."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple

import questionary

from .yaml_util import YamlUtil


def clone_template(destination: str, template_url: str) -> bool:
	"""Clone a template repository to the destination and strip its git history."""
	print(f"Cloning template from {template_url}...")
	try:
		subprocess.run(["git", "clone", template_url, destination], check=True)
		git_dir = Path(destination) / ".git"
		if git_dir.exists():
			shutil.rmtree(git_dir)
		print(f"✓ Template cloned to {destination}")
		return True
	except subprocess.CalledProcessError as error:
		print(f"✗ Failed to clone template: {error}")
		return False


def initialize_git_repo(project_path: Path, remote_url: str) -> bool:
	"""Initialize a git repository, create the first commit, and push to remote."""
	print("\n🐙 Setting up git repository...")
	commands = [
		["git", "init"],
		["git", "add", "."],
		["git", "commit", "-m", "init commit"],
		["git", "branch", "-M", "main"],
		["git", "remote", "add", "origin", remote_url],
		["git", "push", "-u", "origin", "main"],
	]
	for command in commands:
		try:
			subprocess.run(
				command,
				cwd=project_path,
				check=True,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
			)
		except subprocess.CalledProcessError as error:
			print(f"✗ Git step failed: {' '.join(command)}")
			print(error.stderr.decode(errors="ignore"))
			print(
				"⚠️  Git initialization aborted (project files unaffected). You can retry manually."
			)
			return False
	print("✓ Git repository initialized and pushed to 'main'.")
	return True


def get_user_input(prompt: str, default: Optional[str] = None) -> Optional[str]:
	"""Prompt the user for free-form text input."""
	result = questionary.text(prompt, default=default).ask()
	return result if result else None


def get_user_path(prompt: str, default: Optional[str] = None) -> Optional[str]:
	"""Prompt the user for a filesystem path."""
	result = questionary.path(
		prompt,
		default=default or str(Path.cwd()),
		complete_style="readline",
	).ask()
	return result if result else default or str(Path.cwd())


def load_config(init_file: Path) -> Tuple[str, str]:
	"""Read core template configuration from the framework init file."""
	if not init_file.exists():
		raise FileNotFoundError("✗ init.yaml not found!")

	yaml_file = YamlUtil.read_yaml(init_file)
	if not yaml_file:
		raise RuntimeError("✗ Failed to read init.yaml")

	template_url = yaml_file.get("template")
	module_template_url = yaml_file.get("module-template")
	if not template_url:
		raise ValueError("✗ No template URL found in init.yaml!")
	if not module_template_url:
		raise ValueError("✗ No module-template URL found in init.yaml!")

	return str(template_url), str(module_template_url)

