"""CLI entry point — OCR images from the command line.

Uses the same engine layer as the web API (local/cloud/fallback).
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table

from server.engines.local import LocalEngine
from server.engines.cloud import CloudEngine
from server.engines.fallback import FallbackEngine
from server.core.exceptions import OCRError, EngineNotAvailableError

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


def _build_engine(
    mode: str,
    api_key: str | None,
    model: str,
    prompt: str | None,
    device: str,
) -> object:
    """Build an OCR engine from CLI options."""
    if mode == "local":
        return LocalEngine(device=device, enable_table=False)
    elif mode == "cloud":
        key = api_key or os.getenv("ZHIPUAI_API_KEY")
        if not key:
            raise click.UsageError(
                "Cloud engine requires an API key. "
                "Set ZHIPUAI_API_KEY env var or use -k/--api-key."
            )
        return CloudEngine(api_key=key, model=model, prompt=prompt)
    else:  # fallback
        local = LocalEngine(device=device, enable_table=False)
        key = api_key or os.getenv("ZHIPUAI_API_KEY")
        cloud = CloudEngine(api_key=key, model=model, prompt=prompt) if key else None
        return FallbackEngine(local=local, cloud=cloud)


@click.command()
@click.argument(
    "paths", nargs=-1, required=True,
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    "--engine", "-e", default="fallback",
    type=click.Choice(["local", "cloud", "fallback"]),
    help="OCR engine to use (default: fallback — tries local then cloud).",
)
@click.option(
    "-k", "--api-key", default=None,
    help="Zhipu AI API key (or set ZHIPUAI_API_KEY env var).",
)
@click.option(
    "-m", "--model", default="glm-4v-plus",
    help="Cloud model ID (default: glm-4v-plus).",
)
@click.option(
    "-o", "--output", default=None, type=click.Path(path_type=Path),
    help="Output file for results.",
)
@click.option(
    "-p", "--prompt", default=None,
    help="Custom OCR prompt.",
)
@click.option(
    "--device", default="cpu",
    help="Torch device for local engine (default: cpu).",
)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging.")
@click.option("-q", "--quiet", is_flag=True, help="Suppress all output except errors.")
def cli(
    paths: tuple[Path, ...],
    engine: str,
    api_key: str | None,
    model: str,
    output: Path | None,
    prompt: str | None,
    device: str,
    verbose: bool,
    quiet: bool,
) -> None:
    """OCR text from images using local and/or cloud engines.

    PATHS can be one or more image files or directories to scan for images.
    """
    # --- configure logging ---
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
    elif quiet:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.WARNING)

    # --- gather images ---
    image_paths = _gather_images(list(paths))
    if not image_paths:
        console.print("[yellow]No supported image files found.[/]")
        raise SystemExit(0)

    if not quiet:
        console.print(f"[dim]Found {len(image_paths)} image(s)[/]\n")

    # --- build engine ---
    try:
        eng = _build_engine(engine, api_key, model, prompt, device)
    except click.UsageError:
        raise
    except EngineNotAvailableError as e:
        console.print(f"[red]Error:[/] {e}")
        raise SystemExit(1)

    results: dict[Path, str] = {}

    if len(image_paths) == 1:
        # single image — simple path
        p = image_paths[0]
        if not quiet:
            console.print(f"Processing: [bold]{p.name}[/]")
        try:
            result = eng.recognize(p)
            results[p] = result.text
            if not quiet:
                label = f"{p.name}  [{result.engine}]  ({result.elapsed_s:.1f}s)"
                console.print(Panel(result.text.strip() or "(no text)", title=label))
        except Exception as exc:
            logger.exception("Failed: %s", p)
            console.print(f"[red]Error processing {p.name}:[/] {exc}")
            results[p] = ""
    else:
        # batch — with progress bar
        with Progress(transient=not verbose) as progress:
            task = progress.add_task("OCR", total=len(image_paths))
            for i, p in enumerate(image_paths, 1):
                progress.update(task, description=f"[{i}/{len(image_paths)}] {p.name}")
                try:
                    result = eng.recognize(p)
                    results[p] = result.text
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

    # --- write output file ---
    if output:
        lines: list[str] = []
        for p, text in results.items():
            lines.append(f"=== {p.name} ===")
            lines.append(text)
            lines.append("")
        output.write_text("\n".join(lines), encoding="utf-8")
        if not quiet:
            console.print(f"[dim]Results saved to {output}[/]")
