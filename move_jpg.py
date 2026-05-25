import argparse
import shutil
from pathlib import Path
from typing import List

from rich.console import Console
from rich.progress import track

# Define common image extensions to support
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}

def get_unique_path(target_path: Path) -> Path:
    """
    Generates a unique path by appending a counter if a file already exists.
    Example: image.jpg -> image (1).jpg -> image (2).jpg
    """
    counter = 1
    unique_path = target_path
    while unique_path.exists():
        new_name = f"{target_path.stem} ({counter}){target_path.suffix}"
        unique_path = target_path.with_name(new_name)
        counter += 1
    return unique_path

class ImageMover:
    def __init__(self):
        self.console = Console()

    def run(self, source_str: str, dest_str: str) -> None:
        source_dir = Path(source_str).resolve()
        dest_dir = Path(dest_str).resolve()

        if not source_dir.exists():
            self.console.print(f"[bold red]Error:[/bold red] Source folder '{source_dir}' does not exist.")
            return

        if not source_dir.is_dir():
            self.console.print(f"[bold red]Error:[/bold red] Source path '{source_dir}' is not a directory.")
            return

        if dest_dir.exists():
            if not dest_dir.is_dir():
                self.console.print(f"[bold red]Error:[/bold red] Destination '{dest_dir}' already exists as a file.")
                return
            try:
                if source_dir.samefile(dest_dir):
                    self.console.print("[bold red]Error:[/bold red] Source and destination folders cannot be the same.")
                    return
            except OSError:
                pass

        # Gather all image files safely
        try:
            image_files: List[Path] = [
                p for p in source_dir.iterdir()
                if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
            ]
        except PermissionError:
            self.console.print(f"[bold red]Error:[/bold red] Permission denied to read '{source_dir}'.")
            return

        if not image_files:
            self.console.print("[yellow]No image files found in the source directory.[/yellow]")
            return

        # Ensure destination directory exists safely
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            self.console.print(f"[bold red]Error:[/bold red] Permission denied to create destination '{dest_dir}'.")
            return

        self.console.print(f"[cyan]Found {len(image_files)} image(s). Moving to: {dest_dir}[/cyan]")
        
        moved_count = 0
        error_count = 0

        # Move files with a rich progress bar
        for img_path in track(image_files, description="[green]Moving images...[/green]"):
            try:
                target_path = dest_dir / img_path.name
                target_path = get_unique_path(target_path)
                
                shutil.move(str(img_path), str(target_path))
                moved_count += 1
            except PermissionError:
                self.console.print(f"\n[red]Permission denied moving:[/red] {img_path.name}")
                error_count += 1
            except Exception as e:
                self.console.print(f"\n[red]Error moving {img_path.name}:[/red] {e}")
                error_count += 1

        # Summary
        self.console.print("\n[bold]=== Summary ===[/bold]")
        self.console.print(f"Successfully moved: [green]{moved_count}[/green]")
        if error_count > 0:
            self.console.print(f"Failed to move: [red]{error_count}[/red]")
        self.console.print("[bold blue]Done![/bold blue]")

def main() -> None:
    parser = argparse.ArgumentParser(description="A robust tool to move images safely.")
    parser.add_argument("source", nargs="?", help="The source folder containing images.")
    parser.add_argument("dest", nargs="?", help="The destination folder.")
    
    args = parser.parse_args()

    console = Console()
    
    # Interactive fallback if args not provided
    if not args.source:
        console.print("[bold cyan]Image Mover Pro[/bold cyan]")
        source = input("Enter source folder path: ").strip().strip('"').strip("'")
    else:
        source = args.source.strip('"').strip("'")
        
    if not source:
        console.print("[red]Source path cannot be empty.[/red]")
        return
        
    if not args.dest:
        dest = input("Enter destination folder path: ").strip().strip('"').strip("'")
    else:
        dest = args.dest.strip('"').strip("'")
        
    if not dest:
        console.print("[red]Destination path cannot be empty.[/red]")
        return

    mover = ImageMover()
    mover.run(source, dest)

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nOperation cancelled by user. Exiting...")
