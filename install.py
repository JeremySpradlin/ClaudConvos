#!/usr/bin/env python3
"""
Installation script for AI Self-Conversation Experiment Tool
"""

import subprocess
import sys
import os
from pathlib import Path


def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False


def create_config_template():
    """Create a config template file."""
    config_template = {
        "api_key": "",
        "message_limit": 50,
        "message_delay": 2000,
        "max_tokens": 200
    }
    
    config_path = Path("config.json")
    if not config_path.exists():
        import json
        with open(config_path, 'w') as f:
            json.dump(config_template, f, indent=2)
        print("✓ Created config.json template")
    else:
        print("✓ config.json already exists")


def main():
    """Main installation process."""
    print("AI Self-Conversation Experiment Tool - Installation")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create config template
    create_config_template()
    
    print("\n" + "=" * 50)
    print("Installation completed successfully!")
    print("\nNext steps:")
    print("1. Add your Anthropic API key to config.json or enter it in the GUI")
    print("2. Run: python main.py")
    print("\nNote: You can also run the application directly without using config.json")


if __name__ == "__main__":
    main()