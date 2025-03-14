import json
import os
from typing import Any, Dict, Optional

class ConfigValue:
    """A wrapper for configuration values that allows attribute-style access."""
    
    def __init__(self, value: Any):
        self.value = value
    
    def __getattr__(self, key: str) -> 'ConfigValue':
        """Get a nested configuration value using attribute access."""
        if isinstance(self.value, dict) and key in self.value:
            return ConfigValue(self.value[key])
        # Return None-wrapping ConfigValue for missing attributes
        return ConfigValue(None)
    
    def get(self, key: str, default: Any = None) -> 'ConfigValue':
        """Get a nested configuration value using method access."""
        if isinstance(self.value, dict) and key in self.value:
            return ConfigValue(self.value[key])
        return ConfigValue(default)
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __repr__(self) -> str:
        return repr(self.value)
    
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ConfigValue):
            return self.value == other.value
        return self.value == other
    
    # Additional magic methods to make ConfigValue behave more like the wrapped value
    def __bool__(self) -> bool:
        """Return True if the wrapped value is truthy."""
        return bool(self.value)
    
    def __int__(self) -> int:
        """Convert to int if the wrapped value is a number."""
        return int(self.value)
    
    def __float__(self) -> float:
        """Convert to float if the wrapped value is a number."""
        return float(self.value)
    
    def __iter__(self):
        """Support iteration if the wrapped value is iterable."""
        if isinstance(self.value, (list, tuple, dict)):
            return iter(self.value)
        raise TypeError(f"'{type(self.value).__name__}' object is not iterable")
    
    def __getitem__(self, key):
        """Support item access if the wrapped value is a mapping or sequence."""
        if isinstance(self.value, (dict, list, tuple)):
            return ConfigValue(self.value[key])
        raise TypeError(f"'{type(self.value).__name__}' object is not subscriptable")
    
    def __len__(self):
        """Support len() if the wrapped value supports it."""
        if isinstance(self.value, (list, tuple, dict, str)):
            return len(self.value)
        raise TypeError(f"object of type '{type(self.value).__name__}' has no len()")


class ConfigManager:
    """Manager for reading and accessing JSON configuration from a .config file."""
    
    def __init__(self, config_file: str = ".config"):
        """Initialize the ConfigManager.
        
        Args:
            config_file: Path to the configuration file.
        """
        self.config_file = config_file
        self.configs: Dict[str, Any] = {}
        self.load_configs()
    
    def __getattr__(self, key: str) -> ConfigValue:
        """Get a configuration value using attribute access."""
        if key in self.configs:
            return ConfigValue(self.configs[key])
        # Return None-wrapping ConfigValue for missing attributes
        return ConfigValue(None)
    
    def load_configs(self) -> None:
        """Load configuration from the .config file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.configs = json.load(f)
            except json.JSONDecodeError:
                print(f"Error parsing JSON in {self.config_file}")
                self.configs = {}
            except Exception as e:
                print(f"Error loading config file {self.config_file}: {e}")
                self.configs = {}
        else:
            # Create an empty config file if it doesn't exist
            self._save_config()
    
    def get(self, key: str, default: Any = None) -> ConfigValue:
        """Get a configuration value by key.
        
        Args:
            key: Configuration key.
            default: Default value if key not found.
        
        Returns:
            ConfigValue object wrapping the configuration value.
        """
        if key in self.configs:
            return ConfigValue(self.configs[key])
        return ConfigValue(default)
    
    def set_config(self, key: str, value: Any) -> None:
        """Set a configuration value and save it to the file.
        
        Args:
            key: Configuration key.
            value: Value to set.
        """
        self.configs[key] = value
        self._save_config()
    
    def _save_config(self) -> None:
        """Save the configuration to the .config file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.configs, f, indent=2)
        except Exception as e:
            print(f"Error saving config file {self.config_file}: {e}")
