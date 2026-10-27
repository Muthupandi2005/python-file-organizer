# Python File Management Automation

A command-line Python utility that organizes files in a selected folder into extension-based subfolders.

## Features

- Categorizes common document, image, audio, video, spreadsheet, archive, and source-code files.
- Sends unknown file extensions to `Others`.
- Provides a preview by default; preview mode does not move files or create destination folders.
- Requires the explicit `--apply` flag and typing `YES` before moving files.
- Avoids overwriting existing filenames by choosing an unused name.
- Handles invalid folder paths and logs file-operation failures.
- Optional log file output.
- Includes automated unit tests using Python's built-in `unittest` module.

## Requirements

- Python 3.10 or later
- No third-party Python packages required

## Project Structure

```text
python-file-organizer/
├── file_organizer.py
├── README.md
├── .gitignore
└── tests/
    └── test_file_organizer.py
```

## Getting Started

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/python-file-organizer.git
cd python-file-organizer
```

## Usage

### 1. Preview changes (safe default)

Pass the folder path as an argument:

```bash
python file_organizer.py "C:\\Users\\YOUR_USERNAME\\Desktop\\FileOrganizer_Test"
```

If no path is provided, the program asks for one:

```bash
python file_organizer.py
```

### 2. Apply changes

After reviewing the preview, use `--apply` to move files. The program asks you to type `YES` before continuing:

```bash
python file_organizer.py "C:\\Users\\YOUR_USERNAME\\Desktop\\FileOrganizer_Test" --apply
```

### 3. Save a log

```bash
python file_organizer.py "C:\\Users\\YOUR_USERNAME\\Desktop\\FileOrganizer_Test" --log
```

The log is written to `file_organizer.log` in the selected folder. If using `--apply`, combine the options:

```bash
python file_organizer.py "C:\\Users\\YOUR_USERNAME\\Desktop\\FileOrganizer_Test" --apply --log
```

## Run Tests

From the project root:

```bash
python -m unittest discover -s tests -v
```

## Safety Notes

- Test with disposable sample files before using the program on important folders.
- The program organizes files directly inside the selected folder; it does not recursively process nested directories.
- File movement changes file locations and there is no automatic undo feature. Back up important data first.
- Review the preview before running with `--apply`.

## Concepts Demonstrated

- Functions, dictionaries, type hints, and command-line arguments
- File and directory handling with `pathlib`
- Moving files with `shutil`
- Logging and exception handling
- Safe preview / explicit confirmation workflow
- Unit testing with `unittest`
- Git and GitHub version control

## Future Improvements

- Configuration file for custom file categories
- Optional recursive organization
- GUI interface
- File-hash-based duplicate detection
- Summary export to CSV or JSON

## Author

Muthupandi M
