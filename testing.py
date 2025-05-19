import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
import re

def spinner(msg, duration=3):
    symbols = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']
    for _ in range(duration * 4):
        for sym in symbols:
            print(f"\r{msg} {sym}", end="", flush=True)
            time.sleep(0.1)
    print("\r" + " " * (len(msg) + 2), end="\r")

def clear_screen():
    os.system('cls' if sys.platform == 'win32' else 'clear')

def detect_error_reason(stderr_output):
    if "Requires-Python" in stderr_output:
        return "Package requires a different Python version!"
    
    if "Could not find a version that satisfies the requirement" in stderr_output:
        match = re.search(r"😕 Could not find a version that satisfies the requirement (.+?) ", stderr_output)
        if match:
            pkg = match.group(1).strip()
            return f"Failed to download '{pkg}' (not found or incompatible)"
    
    elif "No matching distribution found" in stderr_output:
        return "🚫 Package not available for this Python version or platform"
    
    elif "is not a supported wheel on this platform" in stderr_output:
        return "⚠️ Incompatible wheel or architecture"

    elif "ERROR: Invalid requirement:" in stderr_output:
        match = re.search(r"ERROR: Invalid requirement: '(.+?)'", stderr_output)
        if match:
            return f"❌ Invalid syntax or bad package name: '{match.group(1)}'"
    
    elif "SyntaxError" in stderr_output:
        return "❗ Python script error (check for syntax issues)"
    
    else:
        return "❓ Unknown installation error"

def create_env_and_install_requirements(env_path, failed_envs):
    env_path = Path(env_path).resolve()
    requirements_path = env_path / 'requirements.txt'
    venv_dir = env_path / 'venv'

    print(f"\n🚧 Preparing environment at: {env_path}")

    if not requirements_path.exists():
        print(f"❌ Missing requirements.txt at {env_path}")
        failed_envs.append((str(env_path), "Missing requirements.txt"))
        return

    if venv_dir.exists():
        print(f"♻️ Removing old virtual environment...")
        shutil.rmtree(venv_dir)
        spinner("🧹 Cleaning up: ")

    print("")
    print("🐍 Creating new virtual environment: ")
    spinner("📦 Building environment: ")
    print("")
    subprocess.run([sys.executable, '-m', 'venv', str(venv_dir)], check=True)

    pip_executable = venv_dir / 'bin' / 'pip' if os.name != 'nt' else venv_dir / 'Scripts' / 'pip.exe'

    print("")
    print("📥 Installing packages...")
    try:
        result = subprocess.run(
            [str(pip_executable), 'install', '-r', str(requirements_path)],
            check=True,
            capture_output=True,
            text=True
        )
        print("✅ All packages installed successfully!")
        print("✨ Environment ready!\n")
    except subprocess.CalledProcessError as e:
        reason = detect_error_reason(e.stderr)
        print(f"❌ Installation failed for {env_path}")
        print(f"{reason}")
        print("")
        print("📄 Code Error output:\n")
        print(e.stderr)
        failed_envs.append((str(env_path), reason))

def main():
    print("👋 Welcome to the Python Environment Setup Wizard!")
    time.sleep(0.5)
    print("")

    while True:
        try:
            count = int(input("🔢 How many environments do you need? "))
            if count <= 0:
                print("⚠️ Please enter a positive number.")
                print("❌ Please enter a number greater than 0!")
                print("")
                print("🔄 Resetting in 3 seconds...")
                time.sleep(3)
                continue
            break
        except ValueError:
            print("🚫 Invalid input. Please enter a number.")

    paths = []
    print("\n📥 Enter one path per line (Requries requirements.txt):\n")

    while len(paths) < count:
        entry = input(f"📍 Path {len(paths)+1}: ").strip()
        if entry.lower() == "run":
            print("⚠️ Not enough paths entered. Keep going!")
            continue
        paths.append(entry)

    print()
    print("\n🚀 Activating setup sequence.\n")

    failed_envs = []
    for idx, path in enumerate(paths, 1):
        print(f"\n🔧 Setting up environment {idx}/{count}")
        try:
            create_env_and_install_requirements(path, failed_envs)
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Unexpected error at {path}: {e}")
            failed_envs.append((path, str(e)))

    print("\n🏁 Done!")
    if failed_envs:
        print("⚠️ Some environments had issues:")
        for path, reason in failed_envs:
            print(f" - ❌ {path} ➜ {reason}")
    else:
        print("🎉 All environments created successfully!")

if __name__ == "__main__":
    main()