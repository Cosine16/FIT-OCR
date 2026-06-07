"""CLI entry point for ocr-server."""

import logging
import os
import sys
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table

from .ocr import recognize_image, recognize_images_batch

load_dotenv()

console = Console()
logger = logging.getLogger(__name__)

SUPPORTED_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tiff", ".tif"}


def _gather_images(paths: list[Path]) -> list[Path]:
    """Collect image files from a mix of files and directories."""
    images: list[Path] = []
    for p in paths:
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS:
            images.append(p)
        elif p.is_dir():
            for ext in SUPPORTED_EXTS:
                images.extend(sorted(p.rglob(f"*{ext}")))
        else:
            console.print(f"[yellow]Skipping unsupported path:[/] {p}")
    return sorted(set(images), key=lambda x: x.name)


@click.command()
@click.argument("paths", nargs=-1, required=True, type=click.Path(exists=True, path_type=Path))
@click.option("-k", "--api-key", default=None, help="Zhipu AI API key (or set ZHIPUAI_API_KEY env var).")
@click.option("-m", "--model", default="glm-4v-plus", help="Model ID (default: glm-4v-plus).")
@click.option("-o", "--output", default=None, type=click.Path(path_type=Path), help="Output file for results.")
@click.option("-p", "--prompt", default=None, help="Custom OCR prompt.")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging.")
@click.option("-q", "--quiet", is_flag=True, help="Suppress all output except errors.")
def cli(
    paths: tuple[Path, ...],
    api_key: str | None,
    model: str,
    output: Path | None,
    prompt: str | None,
    verbose: bool,
    quiet: bool,
) -> None:
    """OCR text from images using Zhipu GLM-4V.

    PATHS can be one or more image files or directories to scan for images.
    """
    # --- configure logging ---
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
    elif quiet:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.WARNING)

    # --- API key resolution ---
    api_key = api_key or os.getenv("ZHIPUAI_API_KEY")
    if not api_key:
        console.print(
            "[red]Error:[/] API key required. Set [bold]ZHIPUAI_API_KEY[/] env var or use [bold]-k/--api-key[/]."
        )
        raise SystemExit(1)

    # --- gather images ---
    image_paths = _gather_images(list(paths))
    if not image_paths:
        console.print("[yellow]No supported image files found.[/]")
        raise SystemExit(0)

    if not quiet:
        console.print(f"[dim]Found {len(image_paths)} image(s)[/]\n")

    results: dict[Path, str] = {}

    if len(image_paths) == 1:
        # single image — simple path
        p = image_paths[0]
        if not quiet:
            console.print(f"Processing: [bold]{p.name}[/]")
        text = recognize_image(p, api_key=api_key, model=model, prompt=prompt)
        results[p] = text
        if not quiet:
            console.print(Panel(text.strip() or "(no text)", title=str(p.name)))
    else:
        # batch — with progress bar
        with Progress(transient=not verbose) as progress:
            task = progress.add_task("OCR", total=len(image_paths))
            for i, p in enumerate(image_paths, 1):
                progress.update(task, description=f"[{i}/{len(image_paths)}] {p.name}")
                try:
                    text = recognize_image(p, api_key=api_key, model=model, prompt=prompt)
                    results[p] = text
                except Exception:
                    logger.exception("Failed: %s", p)
                    results[p] = ""
                progress.advance(task)

        # summary table
        if not quiet:
            table = Table(title="OCR Results")
            table.add_column("#", style="dim")
            table.add_column("File")
            table.add_column("Chars", justify="right")
            table.add_column("Preview")
            for i, (p, text) in enumerate(results.items(), 1):
                preview = text[:60].replace("\n", " ") + ("..." if len(text) > 60 else "")
                table.add_row(str(i), str(p.name), str(len(text)), preview)
            console.print(table)

    # --- output ---
    if output:
        out_lines: list[str] = []
        for p, text in results.items():
            out_lines.append(f"=== {p.name} ===")
            out_lines.append(text)
            out_lines.append("")
        output.write_text("\n".join(out_lines), encoding="utf-8")
        if not quiet:
            console.print(f"\n[green]Saved to:[/] {output}")

    # --- exit code ---
    if any(not t for t in results.values()):
        raise SystemExit(1)
