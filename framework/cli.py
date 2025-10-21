import argparse


class ADHDFrameworkCLI:
    """Command Line Interface for the ADHD Framework."""
    
    def __init__(self):
        pass

    @staticmethod
    def show_help(self):
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
        --type <TYPE>                Specify module type (util, manager, plugin, mcp)
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
    
    @staticmethod
    def parser(self) -> argparse.ArgumentParser:
        """Set up and return the argument parser for the CLI."""
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
        return parser