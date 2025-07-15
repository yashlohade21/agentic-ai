#!/usr/bin/env python3
"""
Setup script to configure BinaryBrained API key for the AI Agent system
"""
import os
import sys
from pathlib import Path

def create_env_file():
    """Create or update .env file with BinaryBrained API key"""
    env_file = Path(".env")
    
    print("🔧 Setting up BinaryBrained API configuration...")
    
    # Get API key from user
    api_key = input("\nPlease enter your BinaryBrained API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Exiting.")
        return False
    
    # Create .env content
    env_content = f"""# BinaryBrained API Configuration
BINARYBRAINED_API_KEY={api_key}

# Optional: Other LLM providers
# OPENAI_API_KEY=your_openai_key
# ANTHROPIC_API_KEY=your_anthropic_key
# HUGGINGFACE_API_TOKEN=your_hf_token
# GOOGLE_API_KEY=your_google_key

# System Configuration
LOG_LEVEL=INFO
MAX_CONCURRENT_AGENTS=3
AGENT_TIMEOUT=300
"""
    
    # Write to .env file
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ Created .env file with your BinaryBrained API key")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("\n🔧 Installing required dependencies...")
    
    try:
        import subprocess
        
        # Install requirements
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 BinaryBrained AI Agent Setup")
    print("=" * 30)
    
    # Step 1: Create .env file
    if not create_env_file():
        return
    
    # Step 2: Install dependencies
    if not install_dependencies():
        return
    
    print("\n" + "=" * 30)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run the test: python test_binarybrained_setup.py")
    print("2. If tests pass, start the system: python multi_agent_main.py")
    print("\nNeed help? Check the README.md file for more information.")

if __name__ == "__main__":
    main()
