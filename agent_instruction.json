{
    "project_structure": {
        "root": {
            "description": "Root directory of the ADHD Framework project.",
            "subdirectories": {
                "framework": {
                    "description": "Core framework files (rarely modified)."
                },
                "project": {
                    "description": "Application logic codebase."
                },
                "managers": {
                    "description": "Manager modules.",
                    "agent_instruction": "./managers/[module_name]/agent_instruction.json"
                },
                "utils": {
                    "description": "Utility modules.",
                    "agent_instruction": "./utils/[module_name]/agent_instruction.json"
                },
                "plugins": {
                    "description": "Plugin modules.",
                    "agent_instruction": "./plugins/[module_name]/agent_instruction.json"
                }
            },
            "files": {
                "README.md": "Readme.",
                "LICENSE": "License.",
                "adhd_cli.py": "Main CLI entry point for framework commands.",
                "app.py": "Main application entry point.",
                "agent_instruction.json": "AI agent instruction file for the entire project."
            }
        }
    },
    "valid_module_types": {
        "manager": {
            "location": "./managers/[module_name]",
            "description": "For coordinating external/project-wide systems and shared resources."
        },
        "plugin": {
            "location": "./plugins/[module_name]",
            "description": "For core application logic and framework extensions."
        },
        "util": {
            "location": "./utils/[module_name]",
            "description": "For utility functions and helpers without complex state management."
        }
    },
    "ai_instruction_files_guidelines": [
        "AI agent instruction files, while editing it, you should:",
        "1. Fill all fields",
        "2. Add meaningful usage examples",
        "3. Include only significant core functionality examples",
        "4. Add warnings for important considerations",
        "5. Read source code for full context - don't assume",
        "6. Only edit the file if asked to do so by the user, or auto_documentation is enabled."
    ],
    "ai_agent_auto_coding_setting": {
        "paradigm": "object-oriented programming",
        "rapid_prototyping": {
            "enabled": false,
            "description": "Generate quick prototypes, but they may not be optimal, or they will be hacky."
        },
        "legacy_code": {
            "enabled": false,
            "description": "Generate code that is compatible with existing legacy code when asked to refactor or create functionalities that will be incompatible with the current codebase."
        },
        "auto_testing": {
            "enabled": false,
            "description": "Automatically generate tests for the code and run them."
        },
        "auto_update_agent_instruction_files": {
            "module_agent_instruction_files": false,
            "project_agent_instruction_file": true,
            "description": "Automatically update the agent instruction files."
        },
        "read_instructions": {
            "module_agent_instruction_files": "only_when_relevant",
            "project_agent_instruction_file": true,
            "description": "Read and understand the agent instruction files before performing any actions."
        }
    }
}