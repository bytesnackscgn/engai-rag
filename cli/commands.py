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
    print("\n" + "=" * 60)
    print("Initializing OpenKB Knowledge Base")
    print("=" * 60 + "\n")

    KB_DIR = Path.cwd()
    wiki_dir = KB_DIR / "wiki"
    config_dir = KB_DIR / ".openkb"
    raw_dir = KB_DIR / "raw"

    os.makedirs(config_dir, exist_ok=True)
    os.makedirs(wiki_dir, exist_ok=True)
    os.makedirs(raw_dir, exist_ok=True)

    sources_dir = wiki_dir / "sources"
    summaries_dir = wiki_dir / "summaries"
    concepts_dir = wiki_dir / "concepts"
    explorations_dir = wiki_dir / "explorations"
    reports_dir = wiki_dir / "reports"

    for sub_dir in [sources_dir, summaries_dir, concepts_dir, explorations_dir, reports_dir]:
        os.makedirs(sub_dir, exist_ok=True)

    config_file = config_dir / "config.yaml"
    env_file = KB_DIR / ".env"

    if config_file.exists():
        click.echo(f"✓ Configuration already exists: {config_file}")
    else:
        default_config = {
            "model": os.getenv("LLM_MODEL", "z-ai/glm-4.7-flash"),
            "language": os.getenv("LANGUAGE", "de"),
            "pageindex_threshold": 20,
        }
        with open(config_file, "w") as f:
            if YAML_AVAILABLE:
                yaml.dump(default_config, f, default_flow_style=False)
                click.echo(f"✓ Created configuration: {config_file}")
            else:
                click.echo(f"⚠ Please install PyYAML for YAML config: pip install pyyaml")
                click.echo(f"Writing simple config...")
                with open(config_file, "w") as f:
                    f.write("# OpenKB Configuration\n")
                    f.write(f"model: {default_config['model']}\n")
                    f.write(f"language: {default_config['language']}\n")
                    f.write(f"pageindex_threshold: {default_config['pageindex_threshold']}\n")
                click.echo(f"✓ Created configuration: {config_file}")

    if env_file.exists():
        click.echo(f"✓ Environment file already exists: {env_file}")
    else:
        click.echo(f"⚠ Please create .env file with your API keys:")
        click.echo(f"   - LLM_API_KEY: Your OpenRouter API key")
        click.echo(f"   - OPENROUTER_API_KEY: Your OpenRouter API key")
        click.echo(f"\nExample .env file:")
        click.echo(f"LLM_API_KEY=your_api_key_here")
        click.echo(f"OPENROUTER_API_KEY=your_api_key_here")
        click.echo(f"API_KEY=your_api_key_here")

    click.echo(f"\n✓ OpenKB knowledge base initialized at: {KB_DIR}")
    click.echo(f"  - Wiki directory: {wiki_dir}")
    click.echo(f"  - Raw documents: {raw_dir}")
    click.echo(f"  - Config: {config_file}")
    click.echo(f"\nNext steps:")
    click.echo(f"  1. Add your documents to {raw_dir}/")
    click.echo(f"  2. Run: engaichat openkb add <document>")
    click.echo(f"  3. Query: engaichat openkb query 'your question'")


@openkb.command()
@click.argument("path", type=click.Path(exists=True))
def add(path: str):
    """Add a file or directory to the knowledge base.

    PATH: Path to the file or directory to add. Can be a PDF, MD, DOCX, or directory.
    """
    KB_DIR = Path.cwd()
    wiki_dir = KB_DIR / "wiki"
    raw_dir = KB_DIR / "raw"
    config_file = KB_DIR / ".openkb" / "config.yaml"

    path_obj = Path(path)

    if not path_obj.exists():
        click.echo(f"✗ Path does not exist: {path}")
        sys.exit(1)

    if path_obj.is_file():
        files_to_add = [path_obj]
        rel_path = path_obj.relative_to(raw_dir.parent) if raw_dir.parent in path_obj.parents else path_obj.name
    elif path_obj.is_dir():
        files_to_add = list(path_obj.rglob("*"))
        files_to_add = [f for f in files_to_add if f.is_file()]
        rel_path = path_obj.name
    else:
        click.echo(f"✗ Invalid path: {path}")
        sys.exit(1)

    if not files_to_add:
        click.echo(f"✗ No files found in {path}")
        sys.exit(1)

    click.echo(f"\n📦 Adding {len(files_to_add)} file(s) from {path}")
    click.echo("=" * 60)

    try:
        import openkb
        from openkb import OpenKBClient

        if not config_file.exists():
            click.echo("✗ OpenKB configuration not found. Run 'engaichat openkb init' first.")
            sys.exit(1)

        click.echo(f"✓ OpenKB installed: {openkb.__version__}")
        click.echo(f"✓ Configuration: {config_file}")

        kb = OpenKBClient(config_path=str(config_file))

        for file_path in files_to_add:
            if file_path.suffix.lower() in [".md", ".txt", ".pdf", ".docx", ".html"]:
                click.echo(f"\n➕ Adding: {file_path.name}")
                try:
                    kb.add(file_path)
                    click.echo(f"  ✓ Document indexed: {file_path.name}")
                except Exception as e:
                    click.echo(f"  ✗ Error adding {file_path.name}: {e}")
            else:
                click.echo(f"\n⏭️  Skipping: {file_path.name} (unsupported format)")

        click.echo("\n✓ All documents processed.")

    except ImportError:
        click.echo("✗ OpenKB not installed. Run: pip install openkb")
        sys.exit(1)
    except Exception as e:
        click.echo(f"✗ Error initializing OpenKB: {e}")
        sys.exit(1)


@openkb.command()
@click.argument("question", type=str)
@click.option("--save", is_flag=True, default=False, help="Save answer to wiki/explorations/")
def query(question: str, save: bool = False):
    """Query the knowledge base.

    QUESTION: The question to ask about the knowledge base.
    """
    KB_DIR = Path.cwd()
    config_file = KB_DIR / ".openkb" / "config.yaml"

    if not config_file.exists():
        click.echo("✗ OpenKB configuration not found. Run 'engaichat openkb init' first.")
        sys.exit(1)

    try:
        import openkb
        from openkb import OpenKBClient

        click.echo(f"\n🔍 Querying knowledge base...")
        click.echo(f"Question: {question}\n")

        kb = OpenKBClient(config_path=str(config_file))

        try:
            result = kb.query(question=question)
        except TypeError:
            result = kb.query(question=question, save=save)

        click.echo(f"Answer: {result.answer}")
        click.echo(f"\nConfidence: {result.confidence}")

        if hasattr(result, 'sources') and result.sources:
            click.echo(f"\nSources ({len(result.sources)}):")
            for i, source in enumerate(result.sources[:5], 1):
                click.echo(f"  {i}. {source.get('title', 'Unknown')}")
                click.echo(f"     Page: {source.get('page', 'N/A')}")
                click.echo(f"     Confidence: {source.get('confidence', 0):.2f}")

        if len(result.sources) > 5:
            click.echo(f"  ... and {len(result.sources) - 5} more sources")

        if save:
            try:
                result = kb.query(question=question, save=True)
                click.echo(f"\n✓ Answer saved to: wiki/explorations/exploration_{int(Path(question).stat().st_mtime)}.md")
            except TypeError:
                click.echo("⚠ OpenKB doesn't support --save flag yet. Answer is above.")

    except ImportError:
        click.echo("✗ OpenKB not installed. Run: pip install openkb")
        sys.exit(1)
    except Exception as e:
        click.echo(f"✗ Error querying OpenKB: {e}")
        sys.exit(1)


@openkb.command()
@click.option("--list", "-l", is_flag=True, default=False, help="List all chat sessions")
@click.option("--resume", "-r", type=str, help="Resume a chat session")
@click.option("--delete", "-d", type=str, help="Delete a chat session")
def chat(list: bool = False, resume: Optional[str] = None, delete: Optional[str] = None):
    """Start an interactive chat session with the knowledge base."""
    KB_DIR = Path.cwd()
    config_file = KB_DIR / ".openkb" / "config.yaml"

    if not config_file.exists():
        click.echo("✗ OpenKB configuration not found. Run 'engaichat openkb init' first.")
        sys.exit(1)

    try:
        import openkb
        from openkb import OpenKBClient

        kb = OpenKBClient(config_path=str(config_file))

        if list:
            click.echo("\n📋 Chat Sessions:")
            click.echo("=" * 60)
            try:
                sessions = kb.list_sessions()
                for session in sessions:
                    click.echo(f"  {session}")
            except Exception as e:
                click.echo(f"⚠ Could not list sessions: {e}")
            sys.exit(0)

        if delete:
            click.echo(f"\n🗑️  Deleting chat session: {delete}")
            try:
                kb.delete_session(delete)
                click.echo(f"✓ Session deleted")
            except Exception as e:
                click.echo(f"✗ Error deleting session: {e}")
            sys.exit(0)

        if resume:
            click.echo(f"\n🔄 Resuming chat session: {resume}")
            try:
                kb.chat(resume_session=resume)
            except Exception as e:
                click.echo(f"✗ Error resuming session: {e}")
            sys.exit(0)

        click.echo("\n💬 Interactive Chat Mode")
        click.echo("=" * 60)
        click.echo("Type your message or /help for commands.")
        click.echo("Use Ctrl-D or /exit to quit.\n")

        kb.chat()

    except ImportError:
        click.echo("✗ OpenKB not installed. Run: pip install openkb")
        sys.exit(1)
    except Exception as e:
        click.echo(f"✗ Error starting chat: {e}")
        sys.exit(1)


@openkb.command()
def lint():
    """Run health checks on the knowledge base."""
    KB_DIR = Path.cwd()
    wiki_dir = KB_DIR / "wiki"

    click.echo("\n🔍 Running OpenKB Knowledge Base Lint")
    click.echo("=" * 60)

    if not wiki_dir.exists():
        click.echo("✗ Wiki directory not found. Run 'engaichat openkb init' first.")
        sys.exit(1)

    errors = []
    warnings = []
    info = []

    index_file = wiki_dir / "index.md"
    if not index_file.exists():
        errors.append("Missing index.md")
    else:
        info.append(f"✓ Wiki index exists")

    concepts_dir = wiki_dir / "concepts"
    if concepts_dir.exists():
        concept_count = sum(1 for _ in concepts_dir.glob("*.md"))
        if concept_count == 0:
            warnings.append(f"No concept pages generated yet")
        else:
            info.append(f"✓ {concept_count} concept pages")
    else:
        warnings.append("Missing concepts directory")

    summaries_dir = wiki_dir / "summaries"
    if summaries_dir.exists():
        summary_count = sum(1 for _ in summaries_dir.glob("*.md"))
        info.append(f"✓ {summary_count} document summaries")
    else:
        warnings.append("Missing summaries directory")

    explorations_dir = wiki_dir / "explorations"
    if explorations_dir.exists():
        exploration_count = sum(1 for _ in explorations_dir.glob("*.md"))
        info.append(f"✓ {exploration_count} saved explorations")
    else:
        warnings.append("Missing explorations directory")

    AGENTS_file = wiki_dir / "AGENTS.md"
    if AGENTS_file.exists():
        info.append(f"✓ AGENTS.md exists (wiki governance)")
    else:
        info.append(f"⚠ AGENTS.md not found (wiki schema)")

    if errors:
        click.echo("\n❌ ERRORS:")
        for error in errors:
            click.echo(f"  ✗ {error}")

    if warnings:
        click.echo("\n⚠️  WARNINGS:")
        for warning in warnings:
            click.echo(f"  ⚠ {warning}")

    if info:
        click.echo("\n✅ INFO:")
        for line in info:
            click.echo(f"  {line}")

    click.echo("\n" + "=" * 60)
    if not errors:
        if warnings:
            click.echo(f"ℹ️  Knowledge base has {len(warnings)} warnings")
        else:
            click.echo("✅ Knowledge base looks healthy!")
    else:
        click.echo(f"❌ Knowledge base has {len(errors)} errors")


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


if __name__ == "__main__":
    cli()