# ADHD Framework Agent Instructions

## Project Structure

### Root Directory
Core ADHD Framework project structure:

- **framework/** - Core framework files (rarely modified)
- **project/** - Application logic codebase
- **managers/** - Manager modules (with agent_instruction.json in each)
- **utils/** - Utility modules (with agent_instruction.json in each)
- **plugins/** - Plugin modules (with agent_instruction.json in each)
- **mcps/** - MCP (Model Context Protocol) server modules (with agent_instruction.json in each)
- **adhd_cli.py** - Main CLI entry point for framework commands
- **app.py** - Main application entry point

### Module Structure
Each module contains:

- **__init__.py** - Module initialization (version, folder_path, type, requirements) for ADHD CLI
- **init.yaml** - Module metadata for discovery and management (ADHD CLI)
- **.config_template** - *Optional* configuration templates (JSON format) for Config Manager
- **refresh.py** - *Optional* module state/data refresh script for ADHD CLI

### Valid Module Types

- **manager** (`./managers/[module_name]`) - Coordinating external/project-wide systems and shared resources
- **plugin** (`./plugins/[module_name]`) - Core application logic and framework extensions
- **util** (`./utils/[module_name]`) - Utility functions and helpers without complex state management
- **mcp** (`./mcps/[module_name]`) - Model Context Protocol server implementations


## Agent Response Lifecycle

You must follow the agent response lifecycle to ensure a structured and effective approach to user requests, with the title of each stages and steps clearly printed out in the response.

### 1. Initial Stage
- **Goal Alignment** - Answer the following questions one by one, is the request the following?:
    - Does request make sense? → Continue vs clarify/suggest alternatives
    - Better approach available? → Suggest alternative vs continue
    - Need clarification? → Ask specific questions vs proceed

### 2. Planning Stage
- **Suggest Plan** - List steps to achieve the goal
- **Read Source Code** - If necessary for context and implementation

### 3. Implementation Stage
- **Generate Code / Answer Question** - Implement the request or answer the question
- **Generate Tests** - If auto_testing enabled
- **Generate Debugging** - If auto_debugging enabled
- **Generate Documentation** - If auto_documentation enabled
- **Generate Demo** - If auto_demo enabled

### 4. Finishing Stage
- **Recap** - Summarize actions taken and code generated
- **Suggestions** - Provide improvement recommendations and next steps
- 
## AI Agent Settings

### Working Directories
- **Testing**: `./[module_type]/[module_name]/temp_testing/` or `./temp_testing/`
- **Debugging**: `./[module_type]/[module_name]/temp_debugging/` or `./temp_debugging/`
- **Temporary Files**: `./[module_type]/[module_name]/temp_files/` or `./temp_files/`

### Coding Configuration
- **Paradigm**: Object-oriented programming
- **Rapid Prototyping**: Disabled (prevents hacky/suboptimal code)
- **Docstring Verbosity**: Minimal (one-line if necessary, full if parameters or output are confusing, or logic is complex)
- **Legacy Compatibility**: Disabled
- **Auto Demo**: Disabled
- **Auto Testing**: Disabled
- **Auto Debugging**: Disabled
- **Auto Documentation**: Disabled

## Usage of Config Manager
1. `python adhd_cli.py refresh` - Refresh module states and data, also update the ConfigKeys class.
2. Then access like:
   ```python
   from managers.config_manager import ConfigManager

   cm = ConfigManager()
   api_key_for_abc_plugin = cm.config.ABCPlugin.api_key
   timeout_setting_of_xyz_function_in_def_util = cm.config.DEFUtil.xyz_function.timeout
   ```
3. DO NOT modify the `ConfigManager` or `ConfigKeys` classes directly.
4. DO NOT access like `cm.config['ABCPlugin']['api_key']` or any non-attribute style or assume default values.