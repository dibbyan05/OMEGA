"""
╔══════════════════════════════════════════════════════╗
║        computer/files.py  —  File System Control     ║
║   find · open · create · move · rename · delete      ║
╚══════════════════════════════════════════════════════╝
"""

import os
import sys
import shutil
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

# ─────────────────────────────────────────────────────
#  Search roots — where OMEGA looks for files
# ─────────────────────────────────────────────────────
_SEARCH_ROOTS = [
    Path.home(),
    Path(os.path.expanduser("~\\Desktop")),
    Path(os.path.expanduser("~\\Documents")),
    Path(os.path.expanduser("~\\Downloads")),
    Path(os.path.expanduser("~\\Pictures")),
    Path(os.path.expanduser("~\\Music")),
    Path(os.path.expanduser("~\\Videos")),
]

_SKIP_DIRS = {
    "AppData", "ProgramData", ".git", "__pycache__",
    "node_modules", "Windows", "System32",
}


# ─────────────────────────────────────────────────────
#  Find files
# ─────────────────────────────────────────────────────
def find_files(query: str, limit: int = 5) -> list[str]:
    """
    Search common user directories for files/folders whose names
    contain `query` (case-insensitive).
    Returns a list of absolute path strings (up to `limit`).
    """
    matches: list[str] = []
    query_lower = query.lower()

    seen_roots: set[Path] = set()

    for root in _SEARCH_ROOTS:
        if not root.exists() or root in seen_roots:
            continue
        seen_roots.add(root)

        for dirpath, dirnames, filenames in os.walk(root):
            # Prune skip dirs
            dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]

            for name in filenames + dirnames:
                if query_lower in name.lower():
                    matches.append(os.path.join(dirpath, name))
                    if len(matches) >= limit:
                        return matches

    return matches


# ─────────────────────────────────────────────────────
#  Open folder
# ─────────────────────────────────────────────────────
def open_folder(name: str) -> bool:
    """Open a known folder from FOLDER_MAP by name."""
    path = config.FOLDER_MAP.get(name.lower())
    if path and os.path.exists(path):
        os.startfile(path)
        print(f"[Files] Opened folder: {path}")
        return True
    print(f"[Files] Folder not found: {name}")
    return False


# ─────────────────────────────────────────────────────
#  Create file
# ─────────────────────────────────────────────────────
def create_file(name: str, content: str = "", directory: str = None) -> str:
    """
    Create a new file.
    Defaults to the user's Desktop.
    Returns the full path of the created file.
    """
    directory = directory or os.path.expanduser("~\\Desktop")
    # Ensure a sane extension
    if "." not in name:
        name += ".txt"
    path = os.path.join(directory, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Files] Created: {path}")
    return path


# ─────────────────────────────────────────────────────
#  Create folder
# ─────────────────────────────────────────────────────
def create_folder(name: str, directory: str = None) -> str:
    """
    Create a new folder on the Desktop (or a specified directory).
    Returns the full path.
    """
    directory = directory or os.path.expanduser("~\\Desktop")
    path = os.path.join(directory, name)
    os.makedirs(path, exist_ok=True)
    print(f"[Files] Created folder: {path}")
    return path


# ─────────────────────────────────────────────────────
#  Delete file
# ─────────────────────────────────────────────────────
def delete_file(path: str) -> bool:
    """Delete a file or empty folder."""
    try:
        p = Path(path)
        if p.is_file():
            p.unlink()
        elif p.is_dir():
            shutil.rmtree(p)
        print(f"[Files] Deleted: {path}")
        return True
    except Exception as exc:
        print(f"[Files] Delete error: {exc}")
        return False


# ─────────────────────────────────────────────────────
#  Move file
# ─────────────────────────────────────────────────────
def move_file(source: str, destination: str) -> bool:
    """Move a file or folder to a new location."""
    try:
        # If destination is a known folder alias, resolve it
        dest_resolved = config.FOLDER_MAP.get(destination.lower(), destination)
        shutil.move(source, dest_resolved)
        print(f"[Files] Moved: {source} -> {dest_resolved}")
        return True
    except Exception as exc:
        print(f"[Files] Move error: {exc}")
        return False


# ─────────────────────────────────────────────────────
#  Rename file
# ─────────────────────────────────────────────────────
def rename_file(source: str, new_name: str) -> bool:
    """Rename a file or folder in the same directory."""
    try:
        p      = Path(source)
        target = p.parent / new_name
        p.rename(target)
        print(f"[Files] Renamed: {source} -> {target}")
        return True
    except Exception as exc:
        print(f"[Files] Rename error: {exc}")
        return False
