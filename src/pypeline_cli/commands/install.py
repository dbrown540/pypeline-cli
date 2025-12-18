from pathlib import Path
import subprocess
import platform

import click

from ..core.managers.project_context import ProjectContext


@click.command()
def install():
    """Create .venv if it doesn't exist. Install deps from pyproject.toml"""
    # Verify in pypeline project
    ctx = ProjectContext(start_dir=Path.cwd(), init=False)

    venv_path = ctx.project_root / ".venv"

    # Check if venv already exists
    if venv_path.exists():
        click.echo(f"✓ Virtual environment already exists at {venv_path}")
    else:
        click.echo("📦 Creating virtual environment...")
        subprocess.run(
            ["python", "-m", "venv", ".venv"], cwd=ctx.project_root, check=True
        )
        click.echo(f"✓ Created virtual environment at {venv_path}")

    # Determine pip path based on OS
    if platform.system() == "Windows":
        pip_path = venv_path / "Scripts" / "pip.exe"
    else:
        pip_path = venv_path / "bin" / "pip"

    if not pip_path.exists():
        raise click.ClickException(f"pip not found at {pip_path}")

    # Install project in editable mode using the venv's pip
    click.echo("\n🔧 Installing project dependencies...")
    result = subprocess.run(
        [str(pip_path), "install", "-e", "."],
        cwd=ctx.project_root,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        click.echo(f"❌ Installation failed:\n{result.stderr}")
        raise click.ClickException("Failed to install dependencies")

    click.echo("✅ Successfully installed dependencies!")
    click.echo("\n📂 Next steps:")
    click.echo("  Activate the virtual environment:")
    if platform.system() == "Windows":
        click.echo("    .venv\\Scripts\\activate")
    else:
        click.echo("    source .venv/bin/activate")
