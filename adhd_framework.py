"""
AI Driven Highspeed Development Framework CLI - Simple Template Generator
Clones template, applies module configuration, and initializes project.

USAGE: python adhd-framework.py [OPTIONS]
This script automatically manages its own virtual environment and dependencies.
"""

import sys
from typing import Optional
from pathlib import Path
from framework.cli import ADHDFrameworkCLI as cli
from framework.project_creator import ProjectCreator
from framework.module_creator import ModuleCreator
from framework.listing import ModuleListing
from framework.utils import load_config

# Import our virtual environment manager
from framework.venv_ensurer import VenvEnsurer

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

class ADHDFramework:
    """Main ADHD Framework CLI class"""
    
    def __init__(self):
        self.framework_dir = Path(__file__).parent
        self.template_sets_dir = self.framework_dir / "template_sets"
        self.init_file = self.framework_dir / "init.yaml"
        self.template_url, self.module_template_url = load_config(self.init_file)
        self.project_creator = ProjectCreator(
            template_sets_dir=self.template_sets_dir,
            template_url=self.template_url,
        )
        self.module_creator = ModuleCreator(
            framework_dir=self.framework_dir,
            module_template_url=self.module_template_url,
        )
        self.module_listing = ModuleListing(self.framework_dir)

    def create_module(
        self,
        module_name: Optional[str] = None,
        module_location: Optional[str] = None,
        module_type: Optional[str] = None,
    ) -> bool:
        """Delegate module creation to the ModuleCreator helper."""
        return self.module_creator.create_module(
            module_name=module_name,
            module_location=module_location,
            module_type=module_type,
        )
    
    def create_project(
        self,
        project_name: Optional[str] = None,
        project_location: Optional[str] = None,
        template_set_name: Optional[str] = None,
    ) -> bool:
        """Delegate project creation to the ProjectCreator helper."""
        return self.project_creator.create_project(
            project_name=project_name,
            project_location=project_location,
            template_set_name=template_set_name,
        )
    
    def list_available_modules(self) -> bool:
        """List all available modules from configured listing sources."""
        return self.module_listing.list_available_modules()

def main():
    parser = cli.parser()
    args = parser.parse_args()
    
    # Show help if no arguments or --help flag
    if len(sys.argv) == 1 or args.help:
        cli.show_help()
        return
    
    try:
        framework = ADHDFramework()
        
        if args.create:
            framework.create_project(args.name, args.location, getattr(args, 'template_set'))
        elif args.module:
            framework.create_module(args.name, args.location, getattr(args, 'type'))
        elif getattr(args, 'list', False):
            framework.list_available_modules()
        else:
            print("Unknown command. Use --help for usage information.")
            cli.show_help()
            
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()