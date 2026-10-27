"""
Python File Management Automation
Organizes files in a selected folder by extension.

Safety features:
- Preview before moving files
- Requires explicit confirmation for actual moves
- Avoids overwriting existing files
- Skips directories and symbolic links
- Logs failures and summarizes results
"""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Optional

FILE_CATEGORIES = {
    ".pdf": "PDF_Files",
    ".doc": "Word_Documents",
    ".docx": "Word_Documents",
    ".odt": "Word_Documents",
    ".rtf": "Word_Documents",
    ".txt": "Text_Files",
    ".md": "Text_Files",
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".bmp": "Images",
    ".webp": "Images",
    ".svg": "Images",
    ".mp4": "Videos",
    ".mov": "Videos",
    ".mkv": "Videos",
    ".avi": "Videos",
    ".mp3": "Audio",
    ".wav": "Audio",
    ".aac": "Audio",
    ".flac": "Audio",
    ".csv": "CSV_Files",
    ".xlsx": "Excel_Files",
    ".xls": "Excel_Files",
    ".ods": "Excel_Files",
    ".py": "Python_Files",
    ".ipynb": "Python_Files",
    ".java": "Java_Files",
    ".js": "JavaScript_Files",
    ".html": "Web_Files",
    ".css": "Web_Files",
    ".json": "Data_Files",
    ".xml": "Data_Files",
    ".yaml": "Data_Files",
    ".yml": "Data_Files",
    ".zip": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    ".tar": "Archives",
    ".gz": "Archives",
    ".ppt": "Presentations",
    ".pptx": "Presentations",
    ".odp": "Presentations",
}

LOGGER = logging.getLogger("file_organizer")


def configure_logging(log_file: Optional[Path] = None) -> None:
    """Configure console logging and optional file logging."""
    LOGGER.setLevel(logging.INFO)
    LOGGER.handlers.clear()

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    LOGGER.addHandler(console_handler)

    if log_file is not None:
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            LOGGER.addHandler(file_handler)
        except OSError as exc:
            LOGGER.warning("Could not create log file %s: %s", log_file, exc)


def get_category(file_path: Path) -> str:
    """Return the destination category for a file."""
    return FILE_CATEGORIES.get(file_path.suffix.lower(), "Others")


def get_unique_path(destination: Path) -> Path:
    """Return an unused path without overwriting an existing file."""
    if not destination.exists():
        return destination

    counter = 1
    while True:
        candidate = destination.with_name(
            f"{destination.stem}_{counter}{destination.suffix}"
        )
        if not candidate.exists():
            return candidate
        counter += 1


def list_files(folder: Path) -> list[Path]:
    """List regular files directly inside folder; do not recurse."""
    return sorted(
        (
            item for item in folder.iterdir()
            if item.is_file() and not item.is_symlink()
        ),
        key=lambda item: item.name.lower(),
    )


def build_plan(folder: Path) -> list[tuple[Path, Path]]:
    """Build a list of source and destination paths without changing files."""
    plan = []
    for source in list_files(folder):
        category = get_category(source)
        destination = get_unique_path(folder / category / source.name)
        plan.append((source, destination))
    return plan


def organize_files(folder_path: str | Path, dry_run: bool = True) -> dict:
    """
    Preview or execute organization.

    Returns a result dictionary with counts and failed operations.
    dry_run=True never creates folders or moves files.
    """
    folder = Path(folder_path).expanduser()

    if not folder.exists():
        raise FileNotFoundError(f"Folder does not exist: {folder}")
    if not folder.is_dir():
        raise NotADirectoryError(f"Path is not a folder: {folder}")

    plan = build_plan(folder)
    counts = Counter()
    moved = 0
    failed = []

    if not plan:
        LOGGER.info("No files found in %s", folder)
        return {
            "total": 0,
            "moved": 0,
            "categories": {},
            "failed": [],
            "dry_run": dry_run,
        }

    LOGGER.info("%s: %d file(s) found", "PREVIEW" if dry_run else "ORGANIZING", len(plan))

    for source, destination in plan:
        category = destination.parent.name
        counts[category] += 1
        LOGGER.info("%s -> %s", source.name, destination.relative_to(folder))

        if dry_run:
            continue

        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            safe_destination = get_unique_path(destination)
            shutil.move(str(source), str(safe_destination))
            moved += 1
        except (OSError, shutil.Error) as exc:
            failed.append({"file": source.name, "error": str(exc)})
            LOGGER.error("Could not move %s: %s", source.name, exc)

    if dry_run:
        LOGGER.info("Preview complete. No files were moved.")
    else:
        LOGGER.info("Finished: %d moved, %d failed.", moved, len(failed))

    return {
        "total": len(plan),
        "moved": moved,
        "categories": dict(counts),
        "failed": failed,
        "dry_run": dry_run,
    }


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Organize files in a folder by file extension."
    )
    parser.add_argument(
        "folder",
        nargs="?",
        help="Folder to organize. If omitted, you will be prompted.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually move files. Without this flag, the program only previews.",
    )
    parser.add_argument(
        "--log",
        action="store_true",
        help="Write a file_organizer.log file inside the selected folder.",
    )
    args = parser.parse_args(argv)

    folder_text = args.folder or input("Enter the full path of your test folder: ").strip()
    folder_text = folder_text.strip().strip('"')
    folder = Path(folder_text).expanduser()

    log_path = folder / "file_organizer.log" if args.log else None
    configure_logging(log_path)

    try:
        if args.apply:
            print("WARNING: This will move files in the selected folder.")
            confirmation = input("Type YES to continue: ").strip()
            if confirmation != "YES":
                print("Cancelled. No files were moved.")
                return 0

        result = organize_files(folder, dry_run=not args.apply)
        if result["total"] == 0:
            print("No files to organize.")
        elif args.apply:
            print(f"\nCompleted: {result['moved']} moved, {len(result['failed'])} failed.")
        else:
            print(f"\nPreview ready: {result['total']} file(s). Run with --apply to move them.")
        return 1 if result["failed"] else 0

    except (OSError, ValueError) as exc:
        LOGGER.error("%s", exc)
        return 2


if __name__ == "__main__":
    sys.exit(main())
