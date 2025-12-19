import click
import platform
import shutil
import subprocess
import sys

from pathlib import Path

from ..core.managers.project_context import ProjectContext


@click.command()
def build():
    """Build wheel, sdist, and Snowflake-compatible ZIP distribution"""

    click.echo("\n🚀 Building Snowflake distribution...\n")

    # Find project root
    ctx = ProjectContext(start_dir=Path.cwd(), init=False)
    click.echo(f"📁 Project root: {ctx.project_root}")

    # Determine Python executable - prefer venv if it exists
    venv_path = ctx.project_root / ".venv"
    if platform.system() == "Windows":
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        python_exe = venv_path / "bin" / "python"

    if not python_exe.exists():
        click.echo(
            "⚠️  Virtual environment not found. Run 'pypeline install' first to create it."
        )
        sys.exit(1)

    dist = ctx.project_root / "dist"
    snowflake_dir = dist / "snowflake"

    # Clean the dist folder
    if dist.exists():
        click.echo("🧹 Cleaning dist folder...")
        for item in dist.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

    # Create snowflake directory
    snowflake_dir.mkdir(parents=True, exist_ok=True)

    # Build wheel and sdist
    click.echo("\n🔨 Building distributions...")
    result = subprocess.run(
        [str(python_exe), "-m", "build"],
        cwd=ctx.project_root,
        capture_output=False,
        check=False,
    )

    if result.returncode != 0:
        click.echo("\n❌ Build failed")
        sys.exit(1)

    # Create Snowflake ZIPs from wheels
    # Snowflake stages require special handling:
    # 1. Sometimes reject .whl files, need .zip extension
    # 2. Must have pyproject.toml at top level when unzipped
    # Simply copying .whl to .zip works because wheels ARE zips internally
    # and already have the correct structure
    click.echo("\n📦 Creating Snowflake-compatible ZIPs...")

    zip_count = 0
    for whl in dist.glob("*.whl"):
        zip_file = snowflake_dir / whl.with_suffix(".zip").name
        shutil.copy(whl, zip_file)
        click.echo(f"  ✅ snowflake/{zip_file.name}")
        zip_count += 1

    if zip_count == 0:
        click.echo("  ⚠️  No wheel files found")
        sys.exit(1)

    # Show all distributions
    click.echo("\n📊 Distribution files:")
    click.echo("\n  PyPI distributions:")
    for file in sorted(dist.glob("*.whl")):
        size_kb = file.stat().st_size / 1024
        click.echo(f"    • {file.name:<48} {size_kb:>7.1f} KB")

    for file in sorted(dist.glob("*.tar.gz")):
        size_kb = file.stat().st_size / 1024
        click.echo(f"    • {file.name:<48} {size_kb:>7.1f} KB")

    click.echo("\n  Snowflake distributions:")
    for file in sorted(snowflake_dir.glob("*.zip")):
        size_kb = file.stat().st_size / 1024
        click.echo(f"    • snowflake/{file.name:<40} {size_kb:>7.1f} KB")

    click.echo("\n✅ Build complete!")
    click.echo(
        "\n💡 Upload to Snowflake stage with: PUT file://dist/snowflake/*.zip @your_stage AUTO_COMPRESS=FALSE"
    )
