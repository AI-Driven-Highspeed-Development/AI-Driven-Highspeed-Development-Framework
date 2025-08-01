# ADHD Framework Agent Instructions

## Project Structure

### Root Directory
Core ADHD Framework project structure:

- **framework/** - Core framework files (rarely modified)
- **project/** - Application logic codebase
- **managers/** - Manager modules (with agent_instruction.json in each)
- **utils/** - Utility modules (with agent_instruction.json in each)
- **plugins/** - Plugin modules (with agent_instruction.json in each)
- **adhd_cli.py** - Main CLI entry point for framework commands
- **app.py** - Main application entry point
- **agent_instruction.json** - AI agent instruction file for the entire project

### Module Structure
Each module contains:

- **__init__.py** - Module initialization (version, folder_path, type, requirements) for ADHD CLI
- **agent_instruction.json** - AI agent instruction file for the module
- **init.yaml** - Module metadata for discovery and management (ADHD CLI)
- **.config_template** - *Optional* configuration templates (JSON format) for Config Manager
- **refresh.py** - *Optional* module state/data refresh script for ADHD CLI

### Valid Module Types

- **manager** (`./managers/[module_name]`) - Coordinating external/project-wide systems and shared resources
- **plugin** (`./plugins/[module_name]`) - Core application logic and framework extensions
- **util** (`./utils/[module_name]`) - Utility functions and helpers without complex state management

## AI Agent Settings

### Coding Configuration
- **Paradigm**: Object-oriented programming
- **Rapid Prototyping**: Disabled (prevents hacky/suboptimal code)
- **Docstring Verbosity**: Minimal (one-line if necessary, full if parameters or output are confusing, or logic is complex)
- **Legacy Compatibility**: Disabled
- **Auto Testing**: Disabled
- **Auto Debugging**: Disabled
- **Auto Documentation**: Disabled

### Agent Instruction File Management
- **Auto Update**: Module (disabled), Project (enabled)
- **Read Instructions**: Module (when relevant), Project (always)

### Working Directories
- **Testing**: `./[module_type]/[module_name]/temp_testing/` or `./temp_testing/`
- **Debugging**: `./[module_type]/[module_name]/temp_debugging/` or `./temp_debugging/`

## Agent Response Lifecycle

You must follow the agent response lifecycle to ensure a structured and effective approach to user requests, with the title of each stage clearly printed out in the response.

### 1. Initial Stage
1. **Read Instructions** - Read agent instruction file before any actions
2. **Context Analysis** - Analyze user request and context
3. **Goal Alignment**:
    - Question vs Request → Answer directly vs proceed
    - Does request make sense? → Continue vs clarify/suggest alternatives
    - Better approach available? → Suggest alternative vs continue
    - Need clarification? → Ask specific questions vs proceed

### 2. Planning Stage
- **Suggest Plan** - List steps to achieve the goal
- **Read Module Instructions** - If request relates to specific modules
- **Read Source Code** - If necessary for context and implementation

### 3. Implementation Stage
- **Generate Code** - Implement the request
- **Generate Tests** - If auto_testing enabled
- **Generate Debugging** - If auto_debugging enabled
- **Generate Documentation** - If auto_documentation enabled

### 4. Finishing Stage
- **Recap** - Summarize actions taken and code generated
- **Suggestions** - Provide improvement recommendations and next steps

## AI Instruction File Guidelines

When editing AI agent instruction files:
1. Fill all fields with meaningful key names (replace example_key)
2. Include only significant core functionality examples
3. Add warnings for important considerations
4. Read source code for full context - don't assume
5. Only edit if explicitly asked or auto_documentation is enabled
