#!/usr/bin/env python3
"""
ADHD Framework CLI - Simple Template Generator
Clones template, applies module configuration, and initializes project.
"""

import os
import sys
import argparse
import subprocess
import shutil
import yaml
from pathlib import Path


def clone_template(template_url, destination):
    """Clone the template repository to destination"""
    print(f"Cloning template from {template_url}...")
    try:
        subprocess.run(['git', 'clone', template_url, destination], check=True)
        # Remove .git directory
        git_dir = os.path.join(destination, '.git')
        if os.path.exists(git_dir):
            shutil.rmtree(git_dir)
        print(f"✓ Template cloned to {destination}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to clone template: {e}")
        return False


def list_template_sets():
    """List available template sets"""
    template_dir = Path(__file__).parent / "template_sets"
    if not template_dir.exists():
        print("No template sets found!")
        return []
    
    templates = []
    for yaml_file in template_dir.glob("*.yaml"):
        try:
            with open(yaml_file, 'r') as f:
                config = yaml.safe_load(f)
                if isinstance(config, dict) and 'modules' in config:
                    templates.append({
                        'file': yaml_file.name,
                        'name': config.get('name', yaml_file.stem),
                        'description': config.get('description', 'No description')
                    })
        except Exception as e:
            print(f"Warning: Could not read {yaml_file}: {e}")
    
    return templates


def choose_template_set():
    """Let user choose a template set"""
    templates = list_template_sets()
    
    if not templates:
        print("No template sets available!")
        return None
    
    print("\nAvailable template sets:")
    for i, template in enumerate(templates, 1):
        print(f"{i}. {template['name']}")
        print(f"   {template['description']}")
    
    while True:
        try:
            choice = input(f"\nChoose template set (1-{len(templates)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(templates):
                return templates[idx]['file']
            else:
                print("Invalid choice!")
        except ValueError:
            print("Please enter a number!")


def replace_init_yaml(project_path, template_set_file):
    """Replace init.yaml with chosen template set content"""
    template_sets_dir = Path(__file__).parent / "template_sets"
    template_file = template_sets_dir / template_set_file
    init_file = Path(project_path) / "init.yaml"
    
    if not template_file.exists():
        print(f"✗ Template file not found: {template_file}")
        return False
    
    try:
        shutil.copy2(template_file, init_file)
        print(f"✓ Replaced init.yaml with {template_set_file}")
        return True
    except Exception as e:
        print(f"✗ Failed to replace init.yaml: {e}")
        return False


def run_project_init(project_path):
    """Run project_init.py in the new project"""
    init_script = Path(project_path) / "project_init.py"
    
    if not init_script.exists():
        print(f"✗ project_init.py not found in {project_path}")
        return False
    
    print("Running project initialization...")
    try:
        subprocess.run([sys.executable, str(init_script)], 
                      cwd=project_path, check=True)
        print("✓ Project initialized successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Project initialization failed: {e}")
        return False


def create_project():
    """Main function to create a new project"""
    # Read template URL from init.yaml
    init_file = Path(__file__).parent / "init.yaml"
    if not init_file.exists():
        print("✗ init.yaml not found!")
        return
    
    try:
        with open(init_file, 'r') as f:
            config = yaml.safe_load(f)
            template_url = config.get('template')
            if not template_url:
                print("✗ No template URL found in init.yaml!")
                return
    except Exception as e:
        print(f"✗ Failed to read init.yaml: {e}")
        return
    
    # Get project name and location
    project_name = input("Enter project name: ").strip()
    if not project_name:
        print("✗ Project name cannot be empty!")
        return
    
    project_location = input("Enter project location (press Enter for current directory): ").strip()
    if not project_location:
        project_location = os.getcwd()
    
    project_path = os.path.join(project_location, project_name)
    
    if os.path.exists(project_path):
        print(f"✗ Directory {project_path} already exists!")
        return
    
    # Choose template set
    template_set = choose_template_set()
    if not template_set:
        return
    
    # Create project
    print(f"\nCreating project '{project_name}' at {project_path}")
    
    # 1. Clone template
    if not clone_template(template_url, project_path):
        return
    
    # 2. Replace init.yaml with chosen template set
    if not replace_init_yaml(project_path, template_set):
        return
    
    # 3. Run project_init.py
    if not run_project_init(project_path):
        return
    
    print(f"\n🎉 Project '{project_name}' created successfully!")
    print(f"Location: {project_path}")


def main():
    parser = argparse.ArgumentParser(description="ADHD Framework CLI")
    parser.add_argument('command', nargs='?', default='create', 
                       help='Command to run (default: create)')
    
    args = parser.parse_args()
    
    if args.command == 'create':
        create_project()
    else:
        print(f"Unknown command: {args.command}")
        print("Available commands: create")


if __name__ == "__main__":
    main()