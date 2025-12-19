import click
import shutil
import zipfile

from pathlib import Path

from ..core.managers.project_context import ProjectContext


@click.command()
def build():
    """Create Snowflake-compatible ZIP of project with pyproject.toml at root"""

    click.echo("\n🚀 Building Snowflake distribution...\n")

    # Find project root
    ctx = ProjectContext(start_dir=Path.cwd(), init=False)
    click.echo(f"📁 Project root: {ctx.project_root}")

    # Read project name and version from pyproject.toml
    import tomllib

    with open(ctx.toml_path, "rb") as f:
        toml_data = tomllib.load(f)

    project_name = toml_data["project"]["name"]
    # Get version - either static or dynamic (will be 0.0.0 placeholder if dynamic)
    version = toml_data["project"].get("version", "0.0.0")

    dist = ctx.project_root / "dist"
    snowflake_dir = dist / "snowflake"

    # Clean and create dist directories
    if snowflake_dir.exists():
        click.echo("🧹 Cleaning dist/snowflake folder...")
        shutil.rmtree(snowflake_dir)

    snowflake_dir.mkdir(parents=True, exist_ok=True)

    # Create ZIP filename
    zip_filename = f"{project_name}-{version}.zip"
    zip_path = snowflake_dir / zip_filename

    click.echo(f"\n📦 Creating Snowflake ZIP: {zip_filename}")
    click.echo(
        "   (pyproject.toml will be at root level when unzipped)\n"
    )

    # Files and directories to exclude
    exclude_patterns = {
        ".venv",
        "dist",
        "__pycache__",
        ".pytest_cache",
        ".git",
        ".ruff_cache",
        "htmlcov",
        ".coverage",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".DS_Store",
        ".egg-info",
    }

    def should_exclude(path: Path) -> bool:
        """Check if path should be excluded from ZIP."""
        # Check if any part of the path matches exclude patterns
        for part in path.parts:
            if part in exclude_patterns or part.endswith(".egg-info"):
                return True
        # Check wildcard patterns
        if path.suffix in [".pyc", ".pyo", ".pyd"]:
            return True
        if path.name == ".DS_Store":
            return True
        return False

    # Create ZIP with project files
    # CRITICAL: Files must be added relative to project root so pyproject.toml
    # is at the ZIP root level (not nested in a folder)
    file_count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for item in ctx.project_root.rglob("*"):
            if item.is_file() and not should_exclude(item):
                # Get path relative to project root
                arcname = item.relative_to(ctx.project_root)
                zipf.write(item, arcname)
                file_count += 1

                # Show some files being added (not all to avoid spam)
                if file_count <= 10 or arcname.name == "pyproject.toml":
                    click.echo(f"   ✓ {arcname}")

    if file_count > 10:
        click.echo(f"   ... and {file_count - 10} more files")

    # Show ZIP info
    zip_size_kb = zip_path.stat().st_size / 1024
    click.echo(f"\n📊 Snowflake distribution:")
    click.echo(f"   • snowflake/{zip_filename:<40} {zip_size_kb:>7.1f} KB")
    click.echo(f"   • Total files: {file_count}")

    # Verify pyproject.toml is at root
    with zipfile.ZipFile(zip_path, "r") as zipf:
        if "pyproject.toml" in zipf.namelist():
            click.echo("\n✅ Verified: pyproject.toml is at ZIP root level")
        else:
            click.echo(
                "\n⚠️  Warning: pyproject.toml not found at ZIP root"
            )

    click.echo("\n✅ Build complete!")
    click.echo(
        f"\n💡 Upload to Snowflake stage with:\n   PUT file://dist/snowflake/{zip_filename} @your_stage AUTO_COMPRESS=FALSE"
    )
