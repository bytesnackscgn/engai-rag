"""CLI commands for engai-rag index management."""

import click
import json
import os
from pathlib import Path


@click.group()
def cli():
    """EngAI RAG CLI for index management."""
    pass


@cli.command()
def status():
    """Show system status."""
    click.echo("EngAI RAG Status")
    click.echo("=" * 40)

    # Check OpenKB config
    config_path = Path(".openkb/config.yaml")
    if config_path.exists():
        click.echo(f"✓ OpenKB config: {config_path}")
    else:
        click.echo(f"✗ OpenKB config: NOT FOUND")

    # Check .env
    env_path = Path(".env")
    if env_path.exists():
        click.echo(f"✓ Environment file: {env_path}")
    else:
        click.echo(f"✗ Environment file: NOT FOUND")

    # Check raw documents
    raw_dir = Path("raw")
    if raw_dir.exists():
        doc_count = sum(1 for _ in raw_dir.rglob("*") if _.is_file())
        click.echo(f"✓ Raw documents: {doc_count} files")
    else:
        click.echo(f"✗ Raw documents: NOT FOUND")

    # Check wiki
    wiki_dir = Path("wiki")
    if wiki_dir.exists():
        click.echo(f"✓ Wiki directory: {wiki_dir}")
    else:
        click.echo(f"✗ Wiki directory: NOT FOUND")


@cli.command()
def check():
    """Check index status."""
    click.echo("Checking index status...")

    status_file = Path("cache/index_status.json")
    if not status_file.exists():
        click.echo("Index status file not found. Run 'index run' first.")
        return

    with open(status_file) as f:
        status = json.load(f)

    click.echo(f"Last updated: {status.get('last_updated', 'N/A')}")
    click.echo(f"Total files: {status.get('file_index', {}).get('total_files', 0)}")
    click.echo(f"Indexed files: {status.get('file_index', {}).get('indexed_files', 0)}")
    click.echo(f"Pending files: {status.get('file_index', {}).get('new_files', 0)}")


@cli.command()
def run():
    """Run index on documents."""
    click.echo("Running index...")

    # Check if OpenKB is installed
    try:
        import openkb
        click.echo(f"✓ OpenKB installed: {openkb.__version__}")
    except ImportError:
        click.echo("✗ OpenKB not installed. Run: pip install openkb")
        return

    # Check if documents exist
    raw_dir = Path("raw")
    if not raw_dir.exists():
        click.echo("✗ Raw documents directory not found. Create 'raw/' and add documents.")
        return

    doc_count = sum(1 for _ in raw_dir.rglob("*") if _.is_file())
    if doc_count == 0:
        click.echo("✗ No documents found in raw/ directory.")
        return

    click.echo(f"Found {doc_count} documents to index.")
    click.echo("Note: Full OpenKB integration requires additional setup.")
    click.echo("See SETUP_GUIDE.md for complete instructions.")


@cli.command()
def validate():
    """Validate wiki integrity."""
    click.echo("Validating wiki...")

    wiki_dir = Path("wiki")
    if not wiki_dir.exists():
        click.echo("✗ Wiki directory not found.")
        return

    # Check for index.md
    index_file = wiki_dir / "index.md"
    if index_file.exists():
        click.echo(f"✓ Wiki index: {index_file}")
    else:
        click.echo(f"✗ Wiki index not found.")

    # Check for concepts
    concepts_dir = wiki_dir / "concepts"
    if concepts_dir.exists():
        concept_count = sum(1 for _ in concepts_dir.glob("*.md"))
        click.echo(f"✓ Concepts: {concept_count} files")
    else:
        click.echo(f"✗ Concepts directory not found.")


if __name__ == "__main__":
    cli()