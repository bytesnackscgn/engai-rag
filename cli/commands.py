"""CLI commands for engai-rag with OpenKB integration."""

import click
import json
import os
import sys
from pathlib import Path
import tempfile
from typing import Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


@click.group()
def cli():
    """EngAI RAG CLI for KfW Energy Consultant Assistant."""
    pass


@click.group()
def openkb():
    """OpenKB commands for managing the knowledge base."""
    pass


@openkb.command()
def init():
    """Initialize a new OpenKB knowledge base."""
    import subprocess
    import sys
    
    try:
        result = subprocess.run([sys.executable, "-m", "openkb", "init"], 
                              capture_output=True, text=True, check=True)
        click.echo(result.stdout)
        if result.stderr:
            click.echo(result.stderr, err=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"✗ Failed to initialize OpenKB: {e}")
        if e.stdout:
            click.echo(e.stdout)
        if e.stderr:
            click.echo(e.stderr, err=True)
        sys.exit(1)
    except FileNotFoundError:
        click.echo("✗ OpenKB not installed. Run: pip install openkb")
        sys.exit(1)


@openkb.command()
@click.argument("path", type=click.Path(exists=True))
def add(path: str):
    """Add a file or directory to the knowledge base.

    PATH: Path to the file or directory to add. Can be a PDF, MD, DOCX, or directory.
    """
    import subprocess
    import sys
    
    try:
        # Pass the path argument to the openkb add command
        result = subprocess.run([sys.executable, "-m", "openkb", "add", path], 
                              capture_output=True, text=True, check=True)
        click.echo(result.stdout)
        if result.stderr:
            click.echo(result.stderr, err=True)
    except subprocess.CalledProcessError as e:
        if e.stdout:
            click.echo(e.stdout)
        if e.stderr:
            click.echo(e.stderr, err=True)
        sys.exit(e.returncode)
    except FileNotFoundError:
        click.echo("✗ OpenKB not installed. Run: pip install openkb")
        sys.exit(1)


@openkb.command()
@click.argument("question", type=str)
@click.option("--save", is_flag=True, default=False, help="Save answer to wiki/explorations/")
def query(question: str, save: bool = False):
    """Query the knowledge base.

    QUESTION: The question to ask about the knowledge base.
    """
    import subprocess
    import sys
    
    # Build command arguments
    cmd = [sys.executable, "-m", "openkb", "query", question]
    if save:
        cmd.append("--save")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        click.echo(result.stdout)
        if result.stderr:
            click.echo(result.stderr, err=True)
    except subprocess.CalledProcessError as e:
        if e.stdout:
            click.echo(e.stdout)
        if e.stderr:
            click.echo(e.stderr, err=True)
        sys.exit(e.returncode)
    except FileNotFoundError:
        click.echo("✗ OpenKB not installed. Run: pip install openkb")
        sys.exit(1)


@openkb.command()
@click.option("--list", "-l", is_flag=True, default=False, help="List all chat sessions")
@click.option("--resume", "-r", type=str, help="Resume a chat session")
@click.option("--delete", "-d", type=str, help="Delete a chat session")
def chat(list: bool = False, resume: Optional[str] = None, delete: Optional[str] = None):
    """Start an interactive chat session with the knowledge base."""
    import subprocess
    import sys
    
    # Build command arguments
    cmd = [sys.executable, "-m", "openkb", "chat"]
    if list:
        cmd.append("--list")
    if resume:
        cmd.extend(["--resume", resume])
    if delete:
        cmd.extend(["--delete", delete])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        # For interactive chat, we want to stream the output directly
        if list or resume or delete:
            # Non-interactive modes
            if result.stdout:
                click.echo(result.stdout)
            if result.stderr:
                click.echo(result.stderr, err=True)
            if result.returncode != 0:
                sys.exit(result.returncode)
        else:
            # Interactive mode - run directly
            try:
                subprocess.run([sys.executable, "-m", "openkb", "chat"], check=False)
            except KeyboardInterrupt:
                click.echo("\n👋 Chat session ended.")
                
    except FileNotFoundError:
        click.echo("✗ OpenKB not installed. Run: pip install openkb")
        sys.exit(1)


@openkb.command()
def lint():
    """Run health checks on the knowledge base."""
    import subprocess
    import sys
    
    try:
        result = subprocess.run([sys.executable, "-m", "openkb", "lint"], 
                              capture_output=True, text=True, check=True)
        click.echo(result.stdout)
        if result.stderr:
            click.echo(result.stderr, err=True)
    except subprocess.CalledProcessError as e:
        if e.stdout:
            click.echo(e.stdout)
        if e.stderr:
            click.echo(e.stderr, err=True)
        sys.exit(e.returncode)
    except FileNotFoundError:
        click.echo("✗ OpenKB not installed. Run: pip install openkb")
        sys.exit(1)


@click.command()
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


@click.command()
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


@click.command()
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


@click.command()
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


# Add the openkb subgroup to the main cli group
cli.add_command(openkb)
# Add other commands
cli.add_command(status)
cli.add_command(check)
cli.add_command(run)
cli.add_command(validate)


if __name__ == "__main__":
    cli()