# Markdown to DOCX File Watcher - Setup Instructions

## Overview

This document contains complete instructions for setting up a Python file watcher service that automatically converts `.md` files dropped into the Downloads folder to `.docx` format. The service handles duplicate filenames by archiving existing files with creation-date timestamps.

## Prerequisites

- Python 3.13 installed and available in PATH
- Git installed and configured with GitHub credentials
- GitHub account with ability to create new repositories

## 1. Create GitHub Repository

1.1. Create a new **public** repository on GitHub named `utils`
1.2. Do NOT initialize with README, .gitignore, or license (create empty)
1.3. Note the repository URL: `https://github.com/USERNAME/utils.git`

## 2. Create Local Repository Structure

Execute these commands to create the local folder structure:

```powershell
# Create base directory
$repoPath = "$env:USERPROFILE\repos\utils"
New-Item -ItemType Directory -Path $repoPath -Force
New-Item -ItemType Directory -Path "$repoPath\file-watchers" -Force
New-Item -ItemType Directory -Path "$repoPath\scripts" -Force

Set-Location $repoPath
```

## 3. Create the Python Script

Create the file `file-watchers/md_to_docx_watcher.py` with the following content:

```python
"""
Markdown to DOCX File Watcher
Monitors Downloads folder and converts new .md files to .docx
"""

import os
import time
from datetime import datetime
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pypandoc


# Configuration
WATCH_FOLDER = Path.home() / "Downloads"
DELETE_ORIGINAL = False
OUTPUT_FOLDER = None  # None = same folder as source


def get_file_creation_time(filepath):
    """Get file creation timestamp (Windows) or ctime."""
    stat = filepath.stat()
    # Windows: st_ctime is creation time; Unix: st_ctime is metadata change time
    return datetime.fromtimestamp(stat.st_ctime)


def archive_existing_file(filepath):
    """Rename existing file with its creation date timestamp."""
    if not filepath.exists():
        return
    
    created = get_file_creation_time(filepath)
    timestamp = created.strftime("%Y-%m-%d_%H%M%S")
    archived_name = f"{filepath.stem}_{timestamp}{filepath.suffix}"
    archived_path = filepath.parent / archived_name
    
    # Handle edge case where archived name also exists
    counter = 1
    while archived_path.exists():
        archived_name = f"{filepath.stem}_{timestamp}_{counter}{filepath.suffix}"
        archived_path = filepath.parent / archived_name
        counter += 1
    
    filepath.rename(archived_path)
    print(f"Archived: {filepath.name} -> {archived_name}")


class MarkdownHandler(FileSystemEventHandler):
    """Handles file system events for .md files."""
    
    def on_created(self, event):
        if event.is_directory:
            return
        self._process_file(event.src_path)
    
    def on_moved(self, event):
        if event.is_directory:
            return
        self._process_file(event.dest_path)
    
    def _process_file(self, filepath):
        path = Path(filepath)
        if path.suffix.lower() != '.md':
            return
        
        # Brief delay to ensure file is fully written
        time.sleep(0.5)
        
        output_dir = Path(OUTPUT_FOLDER) if OUTPUT_FOLDER else path.parent
        output_path = output_dir / f"{path.stem}.docx"
        
        try:
            # Archive existing file if present
            archive_existing_file(output_path)
            
            pypandoc.convert_file(
                str(path),
                'docx',
                outputfile=str(output_path)
            )
            print(f"Converted: {path.name} -> {output_path.name}")
            
            if DELETE_ORIGINAL:
                path.unlink()
                print(f"Deleted original: {path.name}")
                
        except Exception as e:
            print(f"Error converting {path.name}: {e}")


def ensure_pandoc():
    """Download pandoc if not installed."""
    try:
        pypandoc.get_pandoc_version()
    except OSError:
        print("Pandoc not found. Downloading...")
        pypandoc.download_pandoc()
        print("Pandoc installed.")


def main():
    ensure_pandoc()
    
    if not WATCH_FOLDER.exists():
        print(f"Watch folder does not exist: {WATCH_FOLDER}")
        return
    
    print(f"Watching: {WATCH_FOLDER}")
    print("Press Ctrl+C to stop")
    
    handler = MarkdownHandler()
    observer = Observer()
    observer.schedule(handler, str(WATCH_FOLDER), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopped.")
    
    observer.join()


if __name__ == "__main__":
    main()
```

## 4. Create requirements.txt

Create the file `requirements.txt` in the repository root with:

```
watchdog
pypandoc
```

## 5. Create README.md

Create `README.md` in the repository root:

```markdown
# Utils

Cross-repository utility scripts and tools.

## Contents

### file-watchers/

- **md_to_docx_watcher.py** - Monitors Downloads folder for .md files and auto-converts to .docx

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python file-watchers/md_to_docx_watcher.py
```
```

## 6. Install Python Dependencies

```powershell
pip install watchdog pypandoc
```

## 7. Initialize Git and Push to GitHub

Replace `USERNAME` with your actual GitHub username:

```powershell
Set-Location "$env:USERPROFILE\repos\utils"

git init
git add .
git commit -m "Add markdown to docx file watcher utility"
git branch -M main
git remote add origin https://github.com/USERNAME/utils.git
git push -u origin main
```

## 8. Create Windows Startup Batch File

Create a `.bat` file in the Windows Startup folder to auto-launch the watcher on login.

8.1. The startup folder location is: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`

8.2. Create the file `md_watcher.bat` in that folder with this content:

```batch
@echo off
pythonw "%USERPROFILE%\repos\utils\file-watchers\md_to_docx_watcher.py"
```

PowerShell command to create this file:

```powershell
$startupFolder = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$batContent = @"
@echo off
pythonw "%USERPROFILE%\repos\utils\file-watchers\md_to_docx_watcher.py"
"@
$batContent | Out-File -FilePath "$startupFolder\md_watcher.bat" -Encoding ASCII
```

## 9. Verify Setup

9.1. Run the watcher manually first to confirm it works:

```powershell
python "$env:USERPROFILE\repos\utils\file-watchers\md_to_docx_watcher.py"
```

9.2. In another window, create a test markdown file in Downloads:

```powershell
"# Test`n`nThis is a test." | Out-File -FilePath "$env:USERPROFILE\Downloads\test_conversion.md" -Encoding UTF8
```

9.3. Confirm `test_conversion.docx` appears in Downloads

9.4. Stop the watcher with Ctrl+C

9.5. Restart your computer (or manually run the .bat) to verify auto-start

## Configuration Options

Edit the top of `md_to_docx_watcher.py` to customize:

| Variable | Default | Description |
|----------|---------|-------------|
| `WATCH_FOLDER` | `~/Downloads` | Folder to monitor |
| `DELETE_ORIGINAL` | `False` | Delete .md after conversion |
| `OUTPUT_FOLDER` | `None` | Output location (None = same as source) |

## Behavior

- Watches for new or moved `.md` files in the configured folder
- If target `.docx` already exists, renames it with creation timestamp (e.g., `report_2025-12-11_143022.docx`)
- Converts new `.md` to `.docx` using Pandoc
- Runs silently in background when launched via `pythonw`

## Troubleshooting

**Pandoc not found**: The script auto-downloads Pandoc on first run. If this fails, install manually from https://pandoc.org/installing.html

**Permission errors**: Ensure the script has write access to Downloads folder

**Not starting on boot**: Verify the .bat file path is correct and `pythonw` is in your PATH
