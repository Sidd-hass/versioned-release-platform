from pathlib import Path


# ============================================================
# DIRECTORIES THAT SHOULD NEVER BE INSPECTED
# ============================================================

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    ".next",
    "coverage",
}


# ============================================================
# FILES THAT ARE USUALLY UNNECESSARY
# ============================================================

IGNORED_FILES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "composer.lock",

    # Documentation that usually doesn't help code review
    "README.md",
    "README.txt",
    "readme.md",

    # Dependency metadata
    "requirements.txt",
}


# ============================================================
# EXTENSIONLESS FILES THAT ARE SAFE TO INSPECT
# ============================================================

ALLOWED_FILENAMES = {
    "Dockerfile",
    "Makefile",
}


# ============================================================
# FILE TYPES THAT THE AGENT CAN INSPECT
# ============================================================

TEXT_EXTENSIONS = {
    # JavaScript / TypeScript
    ".js",
    ".jsx",
    ".ts",
    ".tsx",

    # Python
    ".py",

    # Go
    ".go",

    # Java
    ".java",

    # C / C++
    ".c",
    ".cpp",
    ".h",
    ".hpp",

    # Shell
    ".sh",
    ".bash",

    # Configuration
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".conf",

    # Documentation / text
    ".txt",

    # Web
    ".html",
    ".css",
    ".scss",

    # Database
    ".sql",
}


# ============================================================
# SENSITIVE FILES
# ============================================================

SENSITIVE_FILES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    ".env.test",

    # SSH / credential files
    "id_rsa",
    "id_ed25519",
    "id_dsa",
    "id_ecdsa",

    # Cloud credential files
    "credentials",
}


# ============================================================
# SENSITIVE FILE EXTENSIONS
# ============================================================

SENSITIVE_EXTENSIONS = {
    ".pem",
    ".key",
    ".p12",
    ".pfx",

    # Certificate files
    ".crt",
    ".cer",

    # Private/public key formats
    ".pub",
}


# ============================================================
# REPOSITORY ROOT
# ============================================================

def get_repository_root() -> Path:
    """
    Return the root directory of the project.

    tools.py is located at:

        agents/code-review-agent/tools.py

    Therefore:

        parents[0] = code-review-agent
        parents[1] = agents
        parents[2] = repository root
    """

    return Path(__file__).resolve().parents[2]


# ============================================================
# NORMALIZE PATH
# ============================================================

def normalize_path(path: str) -> Path:
    """
    Convert a user/model supplied path into a normalized Path.
    """

    return Path(path.strip())


# ============================================================
# SAFE PATH CHECK
# ============================================================

def is_safe_path(
    path: Path,
    repository_root: Path,
) -> bool:
    """
    Make sure the requested path:

    - stays inside the repository
    - is not a sensitive file
    - is not inside an ignored directory
    - does not use a sensitive extension
    """

    try:

        path.relative_to(repository_root)

    except ValueError:

        return False


    # --------------------------------------------------------
    # Normalize filename
    # --------------------------------------------------------

    filename = path.name.lower()


    # --------------------------------------------------------
    # Sensitive filename
    # --------------------------------------------------------

    sensitive_files_lower = {
        file_name.lower()
        for file_name in SENSITIVE_FILES
    }

    if filename in sensitive_files_lower:

        return False


    # --------------------------------------------------------
    # Sensitive extension
    # --------------------------------------------------------

    if path.suffix.lower() in SENSITIVE_EXTENSIONS:

        return False


    # --------------------------------------------------------
    # Ignored directories
    # --------------------------------------------------------

    ignored_directories_lower = {
        directory.lower()
        for directory in IGNORED_DIRECTORIES
    }

    for directory in path.parts:

        if directory.lower() in ignored_directories_lower:

            return False


    return True


# ============================================================
# CHECK IF FILE CAN BE INSPECTED
# ============================================================

def is_allowed_file(path: Path) -> bool:
    """
    Determine whether a file is an allowed text/source file.
    """

    filename = path.name.lower()

    ignored_files_lower = {
        file_name.lower()
        for file_name in IGNORED_FILES
    }


    # --------------------------------------------------------
    # Ignore known unnecessary files
    # --------------------------------------------------------

    if filename in ignored_files_lower:

        return False


    # --------------------------------------------------------
    # Allow known extensionless files
    # --------------------------------------------------------

    allowed_filenames_lower = {
        file_name.lower()
        for file_name in ALLOWED_FILENAMES
    }

    if filename in allowed_filenames_lower:

        return True


    # --------------------------------------------------------
    # Allow supported text extensions
    # --------------------------------------------------------

    if path.suffix.lower() in TEXT_EXTENSIONS:

        return True


    return False


# ============================================================
# LIST FILES
# ============================================================

def list_files(directory: str = ".") -> str:
    """
    List useful source-code and configuration files.

    Excludes:

    - Git files
    - virtual environments
    - node_modules
    - build output
    - lock files
    - README files
    - binary files
    - sensitive files
    """

    repository_root = get_repository_root()

    requested_path = normalize_path(directory)


    # --------------------------------------------------------
    # Determine root directory
    # --------------------------------------------------------

    if requested_path == Path("."):

        root = repository_root

    else:

        root = (
            repository_root / requested_path
        ).resolve()


    # --------------------------------------------------------
    # Security check
    # --------------------------------------------------------

    if not is_safe_path(
        root,
        repository_root,
    ):

        raise ValueError(
            "Access to this path is not allowed."
        )


    # --------------------------------------------------------
    # Make sure directory exists
    # --------------------------------------------------------

    if not root.exists():

        raise FileNotFoundError(
            f"Directory not found: {directory}"
        )


    if not root.is_dir():

        raise ValueError(
            f"Not a directory: {directory}"
        )


    files = []


    # --------------------------------------------------------
    # Walk repository
    # --------------------------------------------------------

    for path in root.rglob("*"):

        # Only process files
        if not path.is_file():

            continue


        # Security checks
        if not is_safe_path(
            path,
            repository_root,
        ):

            continue


        # File type / ignore checks
        if not is_allowed_file(path):

            continue


        # Repository-relative path
        relative_path = path.relative_to(
            repository_root
        )


        files.append(
            str(relative_path)
        )


    # --------------------------------------------------------
    # Return sorted result
    # --------------------------------------------------------

    return "\n".join(
        sorted(files)
    )


# ============================================================
# READ FILE
# ============================================================

def read_file(path: str) -> str:
    """
    Read a source-code or configuration file.

    Security restrictions:

    - Cannot read files outside repository
    - Cannot read .env files
    - Cannot read private keys
    - Cannot read certificates
    - Cannot read ignored directories
    - Cannot read binary/unsupported files
    - Cannot read lock files
    - Cannot read README files
    """

    repository_root = get_repository_root()


    # --------------------------------------------------------
    # Normalize requested path
    # --------------------------------------------------------

    requested_path = normalize_path(path)


    # --------------------------------------------------------
    # Resolve against repository root
    # --------------------------------------------------------

    absolute_path = (
        repository_root / requested_path
    ).resolve()


    # --------------------------------------------------------
    # Security check
    # --------------------------------------------------------

    if not is_safe_path(
        absolute_path,
        repository_root,
    ):

        raise PermissionError(
            f"Access denied: {path}"
        )


    # --------------------------------------------------------
    # File existence
    # --------------------------------------------------------

    if not absolute_path.exists():

        raise FileNotFoundError(
            f"File not found: {path}"
        )


    if not absolute_path.is_file():

        raise ValueError(
            f"Not a file: {path}"
        )


    # --------------------------------------------------------
    # Allowed file check
    # --------------------------------------------------------

    if not is_allowed_file(
        absolute_path
    ):

        raise PermissionError(
            f"Access denied: unsupported or unnecessary "
            f"file type: {path}"
        )


    # --------------------------------------------------------
    # Read file
    # --------------------------------------------------------

    return absolute_path.read_text(
        encoding="utf-8",
        errors="replace",
    )


# ============================================================
# LOCAL TESTS
# ============================================================

if __name__ == "__main__":

    print(
        "===== REPOSITORY ROOT ====="
    )

    print(
        get_repository_root()
    )


    print(
        "\n===== FILE LIST ====="
    )

    print(
        list_files()
    )


    print(
        "\n===== TEST READ ====="
    )

    print(
        read_file("backend/server.js")
    )


    print(
        "\n===== DOCKERFILE TEST ====="
    )

    print(
        read_file("backend/Dockerfile")
    )