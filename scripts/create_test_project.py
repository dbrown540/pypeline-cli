#!/usr/bin/env python3
"""
Script to create a test project with dummy inputs for manual inspection.
Creates a project in /tmp, initializes it, creates a pipeline and processor, and runs install.

Usage:
    .venv/bin/python scripts/create_test_project.py
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

# Project configuration
PROJECT_DIR = Path("/tmp/test_pypeline_project")
PROJECT_NAME = "test_etl_project"
PIPELINE_NAME = "sales_data"
PROCESSOR_NAME = "customer_transformer"

# Get the pypeline CLI path from the venv
VENV_BIN = Path(sys.executable).parent
PYPELINE_CLI = str(VENV_BIN / "pypeline")


def run_command(cmd: list[str], cwd: Path | None = None):
    """Run a command with live output."""
    print(f"\n{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    print(f"In directory: {cwd or os.getcwd()}")
    print('='*60 + "\n")
    
    result = subprocess.run(cmd, cwd=cwd)
    
    if result.returncode != 0:
        print(f"\n❌ Command failed with return code {result.returncode}")
        sys.exit(1)
    
    return result


def cleanup():
    """Delete the test project directory."""
    if PROJECT_DIR.exists():
        print(f"🗑️  Removing test project at {PROJECT_DIR}")
        shutil.rmtree(PROJECT_DIR)
        print("✅ Cleanup complete!")
    else:
        print(f"ℹ️  Nothing to clean up - {PROJECT_DIR} does not exist")


def main():
    print(f"Using pypeline CLI: {PYPELINE_CLI}")
    
    # Clean up existing test project
    if PROJECT_DIR.exists():
        print(f"🗑️  Removing existing project at {PROJECT_DIR}")
        shutil.rmtree(PROJECT_DIR)
    
    # Create the parent directory (pypeline init expects it to exist)
    PROJECT_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 Will create project at: {PROJECT_DIR / PROJECT_NAME}")
    
    # Step 1: Initialize project using CLI options (no prompts)
    print("\n" + "="*60)
    print("STEP 1: Initialize Project")
    print("="*60)
    run_command([
        PYPELINE_CLI, "init",
        "--destination", str(PROJECT_DIR),
        "--name", PROJECT_NAME,
        "--author-name", "Test Author",
        "--author-email", "test@example.com",
        "--description", "A test ETL project for manual inspection",
        "--license", "MIT",
        "--company-name", "Test Company",
        "--no-git",
    ])
    
    project_path = PROJECT_DIR / PROJECT_NAME
    
    # Step 2: Run install
    print("\n" + "="*60)
    print("STEP 2: Install Dependencies")
    print("="*60)
    run_command(
        [PYPELINE_CLI, "install"],
        cwd=project_path
    )
    
    # Step 3: Create a pipeline
    print("\n" + "="*60)
    print("STEP 3: Create Pipeline")
    print("="*60)
    run_command(
        [PYPELINE_CLI, "create-pipeline", "--name", PIPELINE_NAME],
        cwd=project_path
    )
    
    # Step 4: Create a processor in the pipeline
    print("\n" + "="*60)
    print("STEP 4: Create Processor")
    print("="*60)
    run_command(
        [PYPELINE_CLI, "create-processor", 
         "--name", PROCESSOR_NAME, 
         "--pipeline", PIPELINE_NAME],
        cwd=project_path
    )
    
    # Print summary
    print(f"\n{'='*60}")
    print("✅ TEST PROJECT CREATED SUCCESSFULLY!")
    print('='*60)
    print(f"\n📂 Project location: {project_path}")
    print(f"\n📋 Project structure:")
    
    # Print directory tree
    for root, dirs, files in os.walk(project_path):
        # Skip __pycache__ and .venv directories
        dirs[:] = [d for d in dirs if d not in ('__pycache__', '.venv', '.git')]
        
        level = root.replace(str(project_path), '').count(os.sep)
        indent = '  ' * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = '  ' * (level + 1)
        for file in files:
            print(f"{subindent}{file}")
    
    print(f"\n🚀 To inspect the project:")
    print(f"  cd {project_path}")
    print(f"  source .venv/bin/activate")
    print(f"  code .  # Open in VS Code")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create or cleanup a test pypeline project")
    parser.add_argument("--cleanup", action="store_true", help="Delete the test project")
    args = parser.parse_args()
    
    if args.cleanup:
        cleanup()
    else:
        main()
