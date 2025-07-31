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
                "adhd_cli.py": "Main CLI entry point for framework commands.",
                "app.py": "Main application entry point.",
                "agent_instruction.json": "AI agent instruction file for the entire project."
            }
        }
    },
    "module_structure": {
        "files": {
            "__init__.py": "Module initialization file, with version, folder_path, type, and requirements, used by ADHD CLI",
            "agent_instruction.json": "AI agent instruction file for the module.",
            "init.yaml": "Module metadata for discovery and management, used by ADHD CLI",
            ".config_template": "Optional, configuration templates with default values for the module, json format, used by Config Manager.",
            "refresh.py": "Optional, to refresh the module state or data, used by ADHD CLI."
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
        "1. Fill all fields, example_key should be replaced with meaningful key names",
        "2. Include only significant core functionality examples",
        "3. Add warnings for important considerations",
        "4. Read source code for full context - don't assume",
        "5. Only edit the file if asked to do so by the user, or auto_documentation is enabled."
    ],
    "ai_agent_auto_coding_setting": {
        "paradigm": "object-oriented programming",
        "rapid_prototyping": {
            "enabled": false,
            "description": "Generate quick prototypes, but they may not be optimal, or they will be hacky."
        },
        "docstring_verbosity": {
            "level": "minimal",
            "options": {
                "none": "No docstrings",
                "minimal": "One-line docstrings if really necessary, full docstrings if params or return values are complex or unclear.",
                "detailed": "Detailed docstrings for all functions and classes."
            }
        },
        "legacy_code_compatibility": {
            "enabled": false,
            "description": "Generate code that is compatible with existing legacy code when asked to refactor or create functionalities that will be incompatible with the current codebase."
        },
        "auto_testing": {
            "enabled": false,
            "description": "Automatically generate tests for the code and run them."
        },
        "auto_debugging": {
            "enabled": false,
            "description": "Automatically generate debugging code to help identify and fix issues in the code."
        },
        "auto_documentation": {
            "enabled": false,
            "description": "Automatically generate documentation for the code, including usage examples and explanations."
        },
        "auto_update_agent_instruction_files": {
            "module": false,
            "project": true,
            "description": "Automatically update the agent instruction files."
        },
        "read_agent_instruction_files": {
            "module": "when_relevant",
            "project": true,
            "options":{
                "always": "Always read instruction.",
                "when_relevant": "Read instruction when you need to call or reference it.",
                "never": "Never read the agent instruction files."
            },
            "description": "Read the agent instruction files before performing any actions."
        },
        "testing_folder": {
            "module": "./[module_type]/[module_name]/temp_testing/",
            "project": "./temp_testing/",
            "description": "Generate testing code in this folder (if permitted)."
        },
        "debugging_folder": {
            "module": "./[module_type]/[module_name]/temp_debugging/",
            "project": "./temp_debugging/",
            "description": "Generate debugging code in this folder (if permitted)."
        }
    },
    "agent_response_lifecycle":{
        "initial_stage": {
            "read_instruction": "Read this agent instruction file before performing any actions.",
            "context_analysis": "Analyze user request and context.",
            "goal_alignment_analysis": {
                "Is the request make sense?": {
                    "Yes": "Continue to the next question.",
                    "No": "Provide a response that explains why the request does not make sense, and suggest alternatives or ask for clarification, then stop. Continue anyway if user insists."
                },
                "Is there any better way to achieve the same goal?": {
                    "Yes": "Suggest the better way, and ask for confirmation to proceed with it.",
                    "No": "Continue to the next question."
                },
                "Is the request too vague that need clarification, so that you can provide response more aligned with user expectations?": {
                    "Yes": "Ask for clarification with specific questions to narrow down the request.",
                    "No": "Continue to the next stage."
                }
            }
        },
        "planning_stage": {
            "suggest_plan": "List the steps you will take to achieve the goal",
            "reading_agent_instruction_files": "If the request is related to a specific module, or will use a module, read the agent instruction file for that module.",
            "reading_source_code": "Read the source code of the module or project if necessary to understand more about the context and how to implement the request."
        },
        "implementation_stage": {
            "generate_code": "Generate the code to implement the request.",
            "generate_tests": "If auto_testing is enabled, generate tests for the code.",
            "generate_debugging_code": "If debugging is enabled, generate debugging code.",
            "generate_documentation": "If auto_documentation is enabled, generate documentation for the code."
        },
        "finishing_stage": {
            "recap": "Recap the actions taken and the code generated.",
            "suggestions": "Provide suggestions for further improvements or next steps."
        }
    }
}