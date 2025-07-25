"""
AI Driven Highspeed Development Framework CLI - Simple Template Generator
Clones template, applies module configuration, and initializes project.

USAGE: python adhd-framework.py [OPTIONS]
This script automatically manages its own virtual environment and dependencies.
"""

from dataclasses import dataclass
import os
import sys
import argparse
import subprocess
import shutil
from typing import List, Optional
from pathlib import Path

# Import our virtual environment manager
from venv_ensurer import VenvEnsurer

def ensure_venv_and_dependencies():
    """Ensure virtual environment exists with required dependencies using VenvEnsurer"""
    requirements_file = Path(__file__).parent / "requirements.txt"
    if requirements_file.exists():
        with open(requirements_file, 'r') as f:
            requirements = [line.strip() for line in f if line.strip()]
    else:
        requirements = ["pyyaml", "questionary"]

    ensurer = VenvEnsurer(
        venv_name=".adhd-venv",
        requirements=requirements,
        config_file="init.yaml"
    )
    
    # If not in managed venv, create/setup and restart
    if not ensurer.is_in_managed_venv():
        ensurer.ensure_venv_and_restart(__file__, sys.argv[1:])

# Ensure we have the right environment before importing dependencies
ensure_venv_and_dependencies()

# Now we can safely import the dependencies
import yaml
import questionary

@dataclass
class ADHDFrameworkTemplateSet:
    """Data class to represent a template set"""
    folder_path: Path
    folder: str = ""
    name: str = ""
    modules: list[str] = None
    description: str = ""

    def __post_init__(self):
        # Extract folder name from path
        self.folder = self.folder_path.name
        # Load init.yaml content
        init_file = self.folder_path / "init.yaml"
        if not init_file.exists():
            raise FileNotFoundError(f"init.yaml not found in {self.folder_path}")
        try:
            with open(init_file, 'r') as f:
                config = yaml.safe_load(f)
                if not isinstance(config, dict):
                    raise ValueError(f"Invalid init.yaml format in {self.folder}")
                if not self.name:
                    self.name = config.get('name', self.folder)
                if self.modules is None:
                    self.modules = config.get('modules', [])
                self.description = config.get('description', 'No description')
        except Exception as e:
            raise RuntimeError(f"Failed to load template set {self.folder}: {e}")


class ADHDFramework:
    """Main ADHD Framework CLI class"""
    
    def __init__(self):
        self.framework_dir = Path(__file__).parent
        self.template_sets_dir = self.framework_dir / "template_sets"
        self.init_file = self.framework_dir / "init.yaml"
        self.template_url = None
        self.module_template_url = None
        self._load_config()
    
    def _load_config(self):
        """Load framework configuration from init.yaml"""
        if not self.init_file.exists():
            raise FileNotFoundError("✗ init.yaml not found!")
        
        try:
            with open(self.init_file, 'r') as f:
                config = yaml.safe_load(f)
                self.template_url = config.get('template')
                self.module_template_url = config.get('module-template')
                if not self.template_url:
                    raise ValueError("✗ No template URL found in init.yaml!")
                if not self.module_template_url:
                    raise ValueError("✗ No module-template URL found in init.yaml!")
        except Exception as e:
            raise RuntimeError(f"✗ Failed to read init.yaml: {e}")
    
    def clone_template(self, destination: str, template_url: str = None) -> bool:
        """Clone the template repository to destination"""
        url = template_url or self.template_url
        print(f"Cloning template from {url}...")
        try:
            subprocess.run(['git', 'clone', url, destination], check=True)
            # Remove .git directory
            git_dir = Path(destination) / '.git'
            if git_dir.exists():
                shutil.rmtree(git_dir)
            print(f"✓ Template cloned to {destination}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to clone template: {e}")
            return False
    
    def list_template_sets(self) -> List[dict]:
        """List available template sets"""
        if not self.template_sets_dir.exists():
            print("No template sets found!")
            return []
        
        templates = []
        for folder_path in self.template_sets_dir.iterdir():
            if folder_path.is_dir():
                try:
                    template_set = ADHDFrameworkTemplateSet(folder_path=folder_path)
                    templates.append({
                        'folder': template_set.folder,
                        'name': template_set.name,
                        'description': template_set.description
                    })
                except Exception as e:
                    print(f"Warning: Could not load template set {folder_path.name}: {e}")
        return templates
    
    def choose_template_set(self) -> Optional[str]:
        """Let user choose a template set interactively"""
        templates = self.list_template_sets()
        
        if not templates:
            print("No template sets available!")
            return None
        
        # Create choices with default option
        choices = []
        default_template = None
        
        for template in templates:
            choice_text = f"{template['name']} - {template['description']}"
            choices.append(choice_text)
            if template['folder'] == 'default':
                default_template = choice_text
        
        # Set default to first template if no 'default' template exists
        if not default_template and choices:
            default_template = choices[0]
        
        selected = questionary.select(
            "Choose template set:",
            choices=choices,
            default=default_template
        ).ask()
        
        if not selected:
            return None
        
        # Find the corresponding folder name
        for template in templates:
            if f"{template['name']} - {template['description']}" == selected:
                return template['folder']
        
        return None
    
    def validate_template_set(self, template_set_name: str) -> bool:
        """Validate that a template set exists"""
        templates = self.list_template_sets()
        for template in templates:
            if template['folder'] == template_set_name:
                return True
        
        available = [t['folder'] for t in templates]
        print(f"✗ Template set '{template_set_name}' not found!")
        print(f"Available template sets: {', '.join(available)}")
        return False
    
    def replace_init_yaml(self, project_path: str, template_set_folder: str) -> bool:
        """Replace init.yaml with chosen template set content"""
        template_file = self.template_sets_dir / template_set_folder / "init.yaml"
        init_file = Path(project_path) / "init.yaml"
        
        if not template_file.exists():
            print(f"✗ Template file not found: {template_file}")
            return False
        
        try:
            shutil.copy2(template_file, init_file)
            print(f"✓ Replaced init.yaml with {template_set_folder}/init.yaml")
            return True
        except Exception as e:
            print(f"✗ Failed to replace init.yaml: {e}")
            return False
    
    def run_project_init(self, project_path: str) -> bool:
        """Run project initialization via the new adhd_cli.py"""
        cli_script = Path(project_path) / "adhd_cli.py"
        
        if not cli_script.exists():
            print(f"✗ adhd_cli.py not found in {project_path}")
            return False
        
        print("Running project initialization via ADHD CLI...")
        try:
            subprocess.run([sys.executable, str(cli_script), "init"], 
                          cwd=project_path, check=True)
            print("✓ Project initialized successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Project initialization failed: {e}")
            return False
    
    def _get_user_input(self, prompt: str, default: str = None) -> Optional[str]:
        """Get text input from user"""
        result = questionary.text(prompt, default=default).ask()
        return result if result else None
    
    def _get_user_path(self, prompt: str, default: str = None) -> Optional[str]:
        """Get path input from user"""
        result = questionary.path(
            prompt,
            default=default or str(Path.cwd()),
            complete_style="readline"
        ).ask()
        return result if result else default or str(Path.cwd())
    
    def _get_module_type(self) -> Optional[str]:
        """Let user choose module type"""
        choices = [
            "util - Utility module with helper functions",
            "manager - Manager module for business logic and coordination",
            "plugin - Plugin module for extending functionality"
        ]
        
        selected = questionary.select(
            "Choose module type:",
            choices=choices,
            default=choices[0]
        ).ask()
        
        if not selected:
            return None
        
        # Extract type from choice (before the " - " separator)
        return selected.split(" - ")[0]
    
    def _create_module_init_yaml(self, module_path: Path, module_name: str, module_type: str) -> bool:
        """Create init.yaml for module with specified structure"""
        folder_path = f"{module_type}s/{module_name}"
        
        init_content = {
            'version': '0.0.1',
            'folder_path': folder_path,
            'type': module_type,
            'requirements': [],
        }
        
        init_file = module_path / "init.yaml"
        try:
            with open(init_file, 'w') as f:
                yaml.dump(init_content, f, default_flow_style=False, sort_keys=False)
            print(f"✓ Created init.yaml with module configuration")
            return True
        except Exception as e:
            print(f"✗ Failed to create init.yaml: {e}")
            return False
    
    def create_module(self, module_name: Optional[str] = None, 
                     module_location: Optional[str] = None, 
                     module_type: Optional[str] = None) -> bool:
        """Main function to create a new module"""
        
        # Get module name (interactive or from parameter)
        if not module_name:
            module_name = self._get_user_input(
                "Enter module name:",
                "new-adhd-module"
            )
        
        if not module_name:
            print("✗ Module name cannot be empty!")
            return False
        
        # Get module location (interactive or from parameter)
        if not module_location:
            module_location = self._get_user_path(
                "Enter module location:"
            )
        
        if not module_location:
            module_location = str(Path.cwd())
        
        # Get module type (interactive or from parameter)
        if not module_type:
            module_type = self._get_module_type()
            if not module_type:
                return False
        
        # Create the full module path
        module_path = Path(module_location) / module_name
        
        # Create parent directories if they don't exist
        module_path.parent.mkdir(parents=True, exist_ok=True)
        
        if module_path.exists():
            print(f"✗ Directory {module_path} already exists!")
            return False
        
        # Create module
        print(f"\nCreating module '{module_name}' at {module_path}")
        
        # 1. Clone module template
        if not self.clone_template(str(module_path), self.module_template_url):
            return False
        
        # 2. Create custom init.yaml for module
        if not self._create_module_init_yaml(module_path, module_name, module_type):
            return False
        
        print(f"\n🎉 Module '{module_name}' created successfully!")
        print(f"Location: {module_path}")
        print(f"Type: {module_type}")
        print(f"Folder path: {module_type}/{module_name}")
        return True
    
    def create_project(self, project_name: Optional[str] = None, 
                      project_location: Optional[str] = None, 
                      template_set_name: Optional[str] = None) -> bool:
        """Main function to create a new project"""
        
        # Get project name (interactive or from parameter)
        if not project_name:
            project_name = self._get_user_input(
                "Enter project name:",
                "new-adhd-project"
            )
        
        if not project_name:
            print("✗ Project name cannot be empty!")
            return False
        
        # Get project location (interactive or from parameter)
        if not project_location:
            project_location = self._get_user_path(
                "Enter project location:"
            )
        
        if not project_location:
            project_location = str(Path.cwd())
        
        # Create the full project path
        project_path = Path(project_location) / project_name
        
        # Create parent directories if they don't exist
        project_path.parent.mkdir(parents=True, exist_ok=True)
        
        if project_path.exists():
            print(f"✗ Directory {project_path} already exists!")
            return False
        
        # Choose template set (interactive or from parameter)
        if template_set_name:
            if not self.validate_template_set(template_set_name):
                return False
            template_set = template_set_name
        else:
            template_set = self.choose_template_set()
            if not template_set:
                return False
        
        # Create project
        print(f"\nCreating project '{project_name}' at {project_path}")
        
        # 1. Clone template
        if not self.clone_template(str(project_path)):
            return False
        
        # 2. Replace init.yaml with chosen template set
        if not self.replace_init_yaml(str(project_path), template_set):
            return False
        
        # 3. Run project_init.py
        if not self.run_project_init(str(project_path)):
            return False
        
        print(f"\n🎉 Project '{project_name}' created successfully!")
        print(f"Location: {project_path}")
        return True


def show_help():
    """Display help information"""
    help_text = """
🚀 ADHD Framework CLI - AI Driven Highspeed Development Framework

USAGE:
    python adhd-framework.py [OPTIONS]

    This script automatically manages its own virtual environment and dependencies.
    On first run, it will create a .adhd-venv folder and install required packages.

OPTIONS:
    -c, --create                 Create a new project (interactive mode)
    -m, --module                 Create a new module (interactive mode)
    -n, --name <NAME>            Specify project/module name
    -l, --location <PATH>        Specify project/module location (default: current directory)
    -t, --template-set <NAME>    Specify template set for projects (default: "default")
    --type <TYPE>                Specify module type (util, manager, plugin)
    -h, --help                   Show this help message

EXAMPLES:
    python adhd-framework.py                                    # Show this help
    python adhd-framework.py --create                           # Interactive project creation
    python adhd-framework.py --module                           # Interactive module creation
    python adhd-framework.py -c -n "my-app"                     # Create project with specific name
    python adhd-framework.py -m -n "my-util" --type "util"      # Create module with specific type
    python adhd-framework.py -c -n "my-app" -l "~/dev"          # Create project with name and location
    python adhd-framework.py -m -n "my-manager" -l "~/modules"  # Create module with name and location
    python adhd-framework.py -c -n "my-app" -t "custom"         # Create project with specific template set

DESCRIPTION:
    The ADHD Framework CLI helps you quickly create new projects and modules using predefined
    templates. It can clone project templates with module configurations, or create standalone
    modules for development.
    
    For projects: Clones a base template, applies module configurations, and initializes
    your project structure using the integrated adhd_cli.py interface.
    
    For modules: Clones a module template and creates an init.yaml with the specified
    module type and folder structure.
    
    After project creation, you can use the project's adhd_cli.py for:
    - Refreshing modules: python adhd_cli.py refresh
    - Listing modules: python adhd_cli.py list
    - Module info: python adhd_cli.py info --module MODULE_NAME
    """
    print(help_text)


def main():
    parser = argparse.ArgumentParser(
        description="ADHD Framework CLI", 
        add_help=False  # We'll handle help manually
    )
    parser.add_argument('-c', '--create', action='store_true', 
                       help='Create a new project')
    parser.add_argument('-m', '--module', action='store_true', 
                       help='Create a new module')
    parser.add_argument('-n', '--name', type=str, 
                       help='Project/module name')
    parser.add_argument('-l', '--location', type=str, 
                       help='Project/module location (default: current directory)')
    parser.add_argument('-t', '--template-set', type=str, 
                       help='Template set name for projects (default: "default")')
    parser.add_argument('--type', type=str, 
                       help='Module type (util, manager, plugin)')
    parser.add_argument('-h', '--help', action='store_true', 
                       help='Show help message')
    
    args = parser.parse_args()
    
    # Show help if no arguments or --help flag
    if len(sys.argv) == 1 or args.help:
        show_help()
        return
    
    try:
        framework = ADHDFramework()
        
        if args.create:
            framework.create_project(args.name, args.location, getattr(args, 'template_set'))
        elif args.module:
            framework.create_module(args.name, args.location, getattr(args, 'type'))
        else:
            print("Unknown command. Use --help for usage information.")
            show_help()
            
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()