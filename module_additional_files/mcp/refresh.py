import json
import os
import re

project_folder = os.path.basename(os.getcwd())
workspace_file = f"{project_folder}.code-workspace"

print(f"Refreshing {workspace_file}...")

def _ensure_key(data: dict, key: str, default_value):
    if key not in data:
        data[key] = default_value

def _chain_ensure_key(data: dict, keys: list, default_value: list):
    """Ensure nested keys exist with corresponding default values."""
    current = data
    for i, key in enumerate(keys):
        _ensure_key(current, key, default_value[i])
        current = current[key]
    return current

def _remove_jsonc_features(raw_content: str) -> str:
        """Strip JSONC-specific syntax such as comments and trailing commas."""
        no_comments = re.sub(r"//.*?$", "", raw_content, flags=re.MULTILINE)
        return re.sub(r",\s*([}\]])", r"\1", no_comments)

def _load_workspace_data(path: str) -> dict:
    with open(path, 'r') as workspace_stream:
        raw_workspace = workspace_stream.read()
    try:
        return json.loads(raw_workspace)
    except json.JSONDecodeError:
        sanitized_workspace = _remove_jsonc_features(raw_workspace)
        try:
            return json.loads(sanitized_workspace)
        except json.JSONDecodeError as decode_error:
            raise RuntimeError(f"Unable to parse workspace file: {path}") from decode_error

if os.path.exists(workspace_file):
    
    workspace_data = _load_workspace_data(workspace_file)

    servers = _chain_ensure_key(workspace_data, ['settings', 'mcp', 'servers'], [{}, {}, {}])

    command = f"${{workspaceFolder:{project_folder}}}/.venv/bin/python"
    args = [f"${{workspaceFolder:{project_folder}}}/mcps/{{module_name}}/{{module_name}}.py"]

    servers['{{module_name}}'] = {
        "type": "stdio",
        "command": command,
        "args": args,
    }

    workspace_data['settings']['mcp']['servers'] = servers

    # Write back the file with normalized JSON formatting
    with open(workspace_file, 'w') as f:
        json.dump(workspace_data, f, indent=4)