"""
Virtual Environment Ensurer - Automatic venv management with Python version validation
Uses the current Python interpreter and validates it meets version requirements.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import re


class VenvEnsurer:
    """Manages virtual environment creation and dependency installation with Python version validation"""
    
    def __init__(self, venv_name: str = ".adhd-venv", requirements: List[str] = None, config_file: str = "init.yaml"):
        self.script_dir = Path(__file__).parent
        self.venv_dir = self.script_dir / venv_name
        self.requirements = requirements or ["pyyaml", "questionary"]
        self.venv_marker = "ADHD_FRAMEWORK_VENV"
        self.config_file = self.script_dir / config_file
        self.python_requirements = self._load_python_requirements()
        
    def _load_python_requirements(self) -> Dict[str, Tuple[int, int]]:
        """Load Python version requirements from config file"""
        default_requirements = {
            "lowest": (3, 10),
            "highest": (3, 12)
        }
        
        if not self.config_file.exists():
            return default_requirements
            
        try:
            # Import yaml here to avoid circular dependency
            import yaml
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
                
            python_config = config.get('python-version', {})
            
            # Parse version strings like "3.10" to tuples like (3, 10)
            lowest_str = str(python_config.get('lowest', '3.10'))
            highest_str = str(python_config.get('highest', '3.12'))
            
            lowest = tuple(map(int, lowest_str.split('.')))[:2]  # Take only major.minor
            highest = tuple(map(int, highest_str.split('.')))[:2]
            
            return {
                "lowest": lowest,
                "highest": highest
            }
        except Exception as e:
            print(f"Warning: Could not load Python requirements from {self.config_file}: {e}")
            return default_requirements
    
    def _get_current_python_version(self) -> Tuple[int, int, int]:
        """Get the current Python interpreter version"""
        return sys.version_info[:3]
    
    def _validate_python_version(self) -> bool:
        """Validate that current Python version meets requirements"""
        current_version = self._get_current_python_version()
        current_major_minor = current_version[:2]
        
        lowest = self.python_requirements["lowest"]
        highest = self.python_requirements["highest"]
        
        if current_major_minor < lowest:
            print(f"✗ Python version too old: {'.'.join(map(str, current_version))}")
            print(f"  Required: Python {'.'.join(map(str, lowest))}+ but ≤ {'.'.join(map(str, highest))}")
            return False
        
        if current_major_minor > highest:
            print(f"✗ Python version too new: {'.'.join(map(str, current_version))}")
            print(f"  Required: Python {'.'.join(map(str, lowest))}+ but ≤ {'.'.join(map(str, highest))}")
            return False
        
        print(f"✓ Python {'.'.join(map(str, current_version))} meets requirements ({'.'.join(map(str, lowest))}+ ≤ {'.'.join(map(str, highest))})")
        return True
    
    def _get_venv_python_path(self) -> Path:
        """Get the Python executable path within the virtual environment"""
        if os.name == 'nt':  # Windows
            return self.venv_dir / "Scripts" / "python.exe"
        else:  # Unix/Linux/Mac
            return self.venv_dir / "bin" / "python"
    
    def _get_venv_pip_path(self) -> Path:
        """Get the pip executable path within the virtual environment"""
        if os.name == 'nt':  # Windows
            return self.venv_dir / "Scripts" / "pip.exe"
        else:  # Unix/Linux/Mac
            return self.venv_dir / "bin" / "pip"
    
    def _create_venv(self) -> bool:
        """Create virtual environment with current Python executable"""
        print("   Creating virtual environment...")
        try:
            subprocess.run([
                sys.executable, "-m", "venv", str(self.venv_dir)
            ], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to create virtual environment: {e}")
            print("  Make sure you have python3-venv installed:")
            print("  - Ubuntu/Debian: sudo apt install python3-venv")
            print("  - Arch Linux: sudo pacman -S python")
            print("  - CentOS/RHEL: sudo yum install python3-venv")
            return False
    
    def _check_dependencies(self) -> List[str]:
        """Check which dependencies need to be installed"""
        venv_python = self._get_venv_python_path()
        if not venv_python.exists():
            return self.requirements
        
        missing_deps = []
        for req in self.requirements:
            # Extract package name (remove version specifiers)
            package_name = req.split('==')[0].split('>=')[0].split('<=')[0].split('<')[0].split('>')[0]
            import_name = package_name.replace('-', '_')
            
            try:
                result = subprocess.run([
                    str(venv_python), "-c", f"import {import_name}"
                ], capture_output=True, check=True)
            except subprocess.CalledProcessError:
                missing_deps.append(req)
        
        return missing_deps
    
    def _install_dependencies(self, dependencies: List[str]) -> bool:
        """Install missing dependencies"""
        if not dependencies:
            return True
        
        venv_pip = self._get_venv_pip_path()
        print(f"   Installing dependencies: {', '.join(dependencies)}")
        
        try:
            subprocess.run([
                str(venv_pip), "install"
            ] + dependencies, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install dependencies: {e}")
            return False
    
    def ensure_venv_and_restart(self, script_path: str, script_args: List[str]) -> None:
        """Ensure virtual environment exists and restart script with venv Python"""
        # Skip if we're already in the managed venv
        if self.venv_marker in os.environ:
            return
        
        print("🔧 Setting up ADHD Framework environment...")
        
        # Validate Python version first
        if not self._validate_python_version():
            print(f"\nPlease install a compatible Python version and try again.")
            sys.exit(1)
        
        # Create venv if it doesn't exist
        if not self.venv_dir.exists():
            if not self._create_venv():
                sys.exit(1)
        
        # Check and install dependencies
        missing_deps = self._check_dependencies()
        if missing_deps:
            if not self._install_dependencies(missing_deps):
                sys.exit(1)
        
        if missing_deps or not self.venv_dir.exists():
            print("✓ Environment setup complete!")
        
        # Re-run script with venv python
        venv_python = self._get_venv_python_path()
        env = os.environ.copy()
        env[self.venv_marker] = "1"
        
        try:
            subprocess.run([str(venv_python), script_path] + script_args, env=env, check=True)
        except subprocess.CalledProcessError as e:
            sys.exit(e.returncode)
        except KeyboardInterrupt:
            print("\n✗ Operation cancelled by user")
            sys.exit(1)
        
        sys.exit(0)
    
    def is_in_managed_venv(self) -> bool:
        """Check if currently running in the managed virtual environment"""
        return self.venv_marker in os.environ
    
    def get_venv_info(self) -> dict:
        """Get information about the virtual environment"""
        venv_python = self._get_venv_python_path()
        current_version = self._get_current_python_version()
        
        info = {
            "venv_exists": self.venv_dir.exists(),
            "venv_path": str(self.venv_dir),
            "python_path": str(venv_python) if venv_python.exists() else None,
            "in_managed_venv": self.is_in_managed_venv(),
            "current_python_version": '.'.join(map(str, current_version)),
            "python_requirements": {
                "lowest": '.'.join(map(str, self.python_requirements["lowest"])),
                "highest": '.'.join(map(str, self.python_requirements["highest"]))
            },
            "version_valid": self._validate_python_version()
        }
        
        if venv_python.exists():
            try:
                result = subprocess.run([
                    str(venv_python), "--version"
                ], capture_output=True, text=True, check=True)
                info["venv_python_version"] = result.stdout.strip()
            except subprocess.CalledProcessError:
                info["venv_python_version"] = "Unknown"
        
        return info


# Convenience function for easy usage
def ensure_venv(requirements: List[str] = None, venv_name: str = ".adhd-venv") -> None:
    """Convenience function to ensure virtual environment and restart if needed"""
    ensurer = VenvEnsurer(venv_name=venv_name, requirements=requirements)
    if not ensurer.is_in_managed_venv():
        ensurer.ensure_venv_and_restart(__file__, sys.argv[1:])


if __name__ == "__main__":
    # Demo/test functionality
    ensurer = VenvEnsurer()
    info = ensurer.get_venv_info()
    
    print("Virtual Environment Information:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    if not ensurer.is_in_managed_venv():
        print("\nTesting Python selection...")
        python_path = ensurer._select_best_python()
        if python_path:
            print(f"Best Python: {python_path}")
