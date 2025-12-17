import re


def validate_project_name(name: str) -> tuple[bool, str]:
    """
    Validate that name is valid for both:
    1. Folder name (cross-platform)
    2. Python package/import name

    Returns: (is_valid, error_message)
    """
    if not name:
        return False, "Project name cannot be empty"

    # Check length
    if len(name) > 255:
        return False, "Project name too long (max 255 characters)"

    # Must be valid Python identifier (package/import name)
    if not name.isidentifier():
        return False, (
            f"'{name}' is not a valid Python identifier. "
            "Must start with letter/underscore, contain only letters, numbers, and underscores"
        )

    # Cannot be a Python keyword
    import keyword

    if keyword.iskeyword(name):
        return False, f"'{name}' is a Python keyword and cannot be used"

    # Check for invalid filesystem characters (cross-platform)
    # Windows forbidden: < > : " / \ | ? *
    # Also avoid spaces for consistency
    invalid_chars = r'[<>:"/\\|?*\s]'
    if re.search(invalid_chars, name):
        return False, f"'{name}' contains invalid characters for folder names"

    # Cannot start with a dot (hidden files/folders)
    if name.startswith("."):
        return False, "Project name cannot start with a dot"

    # Avoid reserved names on Windows
    reserved_names = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    }
    if name.upper() in reserved_names:
        return False, f"'{name}' is a reserved name on Windows"

    return True, ""
