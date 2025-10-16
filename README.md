# AI Driven Highspeed Development Framework

## Overview
The AI Driven Highspeed Development Framework (ADHD Framework) is a command-line tool that accelerates
greenfield project setup and module scaffolding. It clones pre-configured templates, injects project or
module metadata, and optionally initializes a Git repository so teams can move from idea to working
code in minutes.

## Key Features
- Automatic virtual environment management via `venv_ensurer.VenvEnsurer`
- Interactive project creation backed by template sets stored in `template_sets/`
- Module scaffolding with generated `.config_template` and starter Python class
- Optional GitHub repository initialization for both projects and modules
- Extensible template sources that can live locally or in remote Git repositories

## Requirements
- Python 3.10 – 3.12 (validated by `init.yaml`)
- Access to the template repositories referenced in `init.yaml`
- Internet connectivity when cloning remote templates

Python dependencies are kept minimal and specified in `requirements.txt`:

```
pyyaml
questionary
```

These are installed automatically inside `.adhd-venv` the first time you run the CLI.

## Quick Start
1. Clone this repository and `cd` into `AI-Driven-Highspeed-Development-Framework/`.
2. Run `python adhd_framework.py --help` for a feature overview.
3. Create a project interactively: `python adhd_framework.py --create`.
4. Create a module interactively: `python adhd_framework.py --module`.

The CLI will create `.adhd-venv/` if necessary, install requirements, and re-launch itself from the
managed environment.

## Command Reference
- `python adhd_framework.py --create [-n NAME] [-l PATH] [-t TEMPLATE_SET]`
	- Clones the selected project template, applies the chosen template set, and runs the generated
		project's `adhd_cli.py` to finish initialization.
- `python adhd_framework.py --module [-n NAME] [-l PATH] [--type {util|manager|plugin}]`
	- Clones the module template, writes a tailored `init.yaml`, and copies templated scaffolding files.
- `python adhd_framework.py --help`
	- Displays CLI help, argument descriptions, and usage examples.

During project or module creation, the CLI prompts for an optional GitHub remote URL. Supplying a URL
triggers `git init`, adds the generated files, and pushes the first commit to the remote.

## Template Sets
- Template repositories are defined in `init.yaml`:
	- `template`: default project template (`Default-Project-Template`)
	- `module-template`: default module template (`Default-Module-Template`)
- Additional template sets can be added under `template_sets/<set_name>/init.yaml` with custom
	metadata (e.g., description, module list, alternate template repo).
- `adhd_framework.py` reads these definitions and lets you choose the desired set at runtime.

## Module Scaffolding Details
When a module is created, `_add_generated_files_to_new_module` copies and personalizes assets from
`gen_template/`:
- `.config_template` – JSON structure for Config Manager integration
- `<module_name>.py` – sample module class wired to `ConfigManager`

Placeholders `{{module_name}}` and `{{ModuleNameToCamelCase}}` are replaced automatically so the files
match the module you created.

## Customization Tips
- Update `template_sets/default/init.yaml` or add new folders to distribute multiple project
	blueprints (e.g., REST API, data pipeline, utilities).
- Customize the module scaffolding by editing the source templates under `gen_template/`.
- Adjust dependency requirements in `requirements.txt`; the CLI will install them on the next run.

## Development Workflow
1. Modify templates or CLI behavior.
2. Run `python adhd_framework.py --module` or `--create` against a scratch directory.
3. Verify generated artifacts and optional Git initialization.
4. Commit changes once validation passes.

Future enhancements can include expanding template metadata, adding validation hooks, or wiring in
automated tests from within the CLI.
