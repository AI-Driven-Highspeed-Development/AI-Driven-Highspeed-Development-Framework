#!/usr/bin/env python3

import os
import sys
import shutil
import re
import argparse
from pathlib import Path
import questionary
from typing import List, Dict

# Path constants (relative to script directory)
PROJECT_TEMPLATES_DIR = "project_templates"
MODULE_TEMPLATES_DIR = "module_templates"
DEFAULT_PROJECT_TEMPLATE = "default"
DEFAULT_MODULE_TEMPLATE = "default"
DEFAULT_PROJECTS_DIR = str(Path.home() / "Projects")

# Global path variables to be initialized at runtime
PATHS: Dict[str, Path] = {}

def init_paths():
    """Initialize all absolute paths based on the script location"""
    script_dir = Path(__file__).parent.absolute()
    
    PATHS["SCRIPT_DIR"] = script_dir
    PATHS["PROJECT_TEMPLATES"] = script_dir / PROJECT_TEMPLATES_DIR
    PATHS["MODULE_TEMPLATES"] = script_dir / MODULE_TEMPLATES_DIR
    PATHS["DEFAULT_PROJECTS"] = Path(DEFAULT_PROJECTS_DIR)

def validate_project_name(name):
    """
    Validate that the project name is compatible with GitHub repository naming conventions.
    """
    if not name or name.strip() == "":
        return False
    
    pattern = r'^[a-zA-Z0-9._-]+$'
    if not re.match(pattern, name):
        return False
    if name.endswith('.git'):
        return False
    return True

def get_available_templates(templates_dir: Path) -> List[str]:
    """
    Get list of available templates from a directory
    """
    if not templates_dir.exists():
        return []
    
    return [item.name for item in templates_dir.iterdir() if item.is_dir()]

def create_project(project_name, target_dir=None, project_template=DEFAULT_PROJECT_TEMPLATE, module_templates=None):
    """
    Create a new project with the given name:
    1. Create the project directory
    2. Copy template files from project_templates/{project_template}
    3. Copy selected module templates into project module folder
    """
    # Define paths
    if target_dir:
        project_path = Path(target_dir) / project_name
    else:
        project_path = Path.cwd() / project_name
    
    template_path = PATHS["PROJECT_TEMPLATES"] / project_template
    
    # Check if template directory exists
    if not template_path.exists():
        print(f"❌ Error: Template directory {template_path} not found.")
        return False
    
    # Check if project directory already exists
    if project_path.exists():
        print(f"❌ Error: Project directory {project_path} already exists.")
        return False
    
    try:
        # Create project directory
        project_path.mkdir(parents=True, exist_ok=False)
        print(f"📁 Creating project directory: {project_path}")
        
        # Copy template files to project directory
        print(f"📋 Applying {project_template} project template...")
        for item in template_path.iterdir():
            if item.is_dir():
                shutil.copytree(item, project_path / item.name)
            else:
                shutil.copy2(item, project_path / item.name)
        
        # Create modules directory if it doesn't exist in the template
        modules_dir = project_path / "modules"
        modules_dir.mkdir(exist_ok=True)
        
        # Copy selected module templates into project module folder
        if not module_templates:
            module_templates = [DEFAULT_MODULE_TEMPLATE]
            
        for module_template in module_templates:
            module_template_path = PATHS["MODULE_TEMPLATES"] / module_template
            if module_template_path.exists():
                module_dest = modules_dir / module_template
                print(f"📦 Adding {module_template} module...")
                shutil.copytree(module_template_path, module_dest)
            else:
                print(f"⚠️  Warning: Module template {module_template} not found.")
        
        print(f"✅ Project '{project_name}' created successfully at {project_path}")
        return True
    
    except Exception as e:
        print(f"❌ Error creating project: {e}")
        return False

def main():
    # Initialize paths at the start of the program
    init_paths()
    
    parser = argparse.ArgumentParser(
        description="✨ AI-Driven Highspeed Development Framework (ADHD-Framework) CLI ✨"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Create project command
    create_parser = subparsers.add_parser("create", help="🚀 Create a new project")
    create_parser.add_argument("project_name", nargs="?", help="Name of the project")
    create_parser.add_argument("--template", "-t", help="Project template to use")
    create_parser.add_argument("--modules", "-m", nargs="+", help="Module templates to include")
    create_parser.add_argument("--dir", "-d", help="Target directory for project")
    
    args = parser.parse_args()
    
    if args.command == "create":
        print("🚀 Welcome to ADHD-Framework Project Creator! 🚀")
        
        # Ask for project name if not provided
        if not args.project_name:
            project_name = questionary.text(
                "Enter project name (GitHub repo compatible):",
                validate=lambda text: validate_project_name(text) or "Please enter a valid non-empty name"
            ).ask()
            
            # Handle case where questionary is exited with Ctrl+C
            if not project_name:
                print("❌ Project creation cancelled.")
                return
        else:
            project_name = args.project_name
            if not validate_project_name(project_name):
                print("❌ Invalid project name. Please use only letters, numbers, hyphens, underscores, and periods.")
                print("   The name should not be empty and should not end with '.git'.")
                return
        
        # If we're in the script directory, ask for a target directory
        target_dir = args.dir
        if Path.cwd() == PATHS["SCRIPT_DIR"] and not target_dir:
            should_ask = questionary.confirm(
                "⚠️  You're running the CLI from its installation directory. Would you like to specify a different target directory?",
                default=True
            ).ask()
            
            if should_ask:
                target_dir = questionary.text(
                    "Enter target directory path:",
                    default=DEFAULT_PROJECTS_DIR
                ).ask()
                
                # Create target directory if it doesn't exist
                target_path = Path(target_dir)
                if not target_path.exists():
                    create_dir = questionary.confirm(
                        f"Directory {target_dir} doesn't exist. Create it?",
                        default=True
                    ).ask()
                    
                    if create_dir:
                        target_path.mkdir(parents=True, exist_ok=True)
                    else:
                        print("❌ Aborted: Target directory doesn't exist.")
                        return
        
        # Select project template
        available_project_templates = get_available_templates(PATHS["PROJECT_TEMPLATES"])
        if not available_project_templates:
            print("❌ No project templates found in project_templates directory.")
            return
        
        if not args.template:
            project_template = questionary.select(
                "🎨 Select a project template:",
                choices=available_project_templates,
                default=DEFAULT_PROJECT_TEMPLATE if DEFAULT_PROJECT_TEMPLATE in available_project_templates else available_project_templates[0]
            ).ask()
        else:
            project_template = args.template
            if project_template not in available_project_templates:
                print(f"❌ Project template '{project_template}' not found.")
                return
            
        # Select module templates
        available_module_templates = get_available_templates(PATHS["MODULE_TEMPLATES"])
        if not available_module_templates:
            print("⚠️  No module templates found in module_templates directory.")
            module_templates = []
        elif not args.modules:
            module_templates = questionary.checkbox(
                "📦 Select module templates to include:",
                choices=available_module_templates,
                default=[DEFAULT_MODULE_TEMPLATE] if DEFAULT_MODULE_TEMPLATE in available_module_templates else []
            ).ask()
        else:
            module_templates = args.modules
            for module in module_templates:
                if module not in available_module_templates:
                    print(f"⚠️  Module template '{module}' not found and will be skipped.")
            module_templates = [m for m in module_templates if m in available_module_templates]
        
        create_project(project_name, target_dir, project_template, module_templates)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
