#!/usr/bin/env python3
"""Test script to verify Click command registration."""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing Click command registration...\n")

# Import the CLI module
try:
    from cli import commands
    print("✓ Successfully imported cli.commands")

    # Check if the cli group exists
    if hasattr(commands, 'cli'):
        print("✓ CLI group found")
        print(f"  CLI name: {commands.cli.name}")

        # Check if openkb subcommand exists
        if hasattr(commands.cli, 'add_command'):
            # Check if openkb is registered
            try:
                openkb_cmd = commands.cli.get_command(None, 'openkb')
                if openkb_cmd:
                    print("✓ openkb subcommand group found")
                    print(f"  openkb name: {openkb_cmd.name}")

                    # Check subcommands
                    if hasattr(openkb_cmd, 'list_commands'):
                        subcommands = openkb_cmd.list_commands(None)
                        print(f"✓ Found {len(subcommands)} subcommands:")
                        for cmd in subcommands:
                            print(f"  - {cmd}")

                        if 'init' in subcommands:
                            print("✓ init subcommand found")
                        if 'add' in subcommands:
                            print("✓ add subcommand found")
                        if 'query' in subcommands:
                            print("✓ query subcommand found")
                        if 'chat' in subcommands:
                            print("✓ chat subcommand found")
                        if 'lint' in subcommands:
                            print("✓ lint subcommand found")
                    else:
                        print("✗ openkb group doesn't have list_commands method")

                else:
                    print("✗ openkb subcommand group NOT found!")
            except Exception as e:
                print(f"✗ Error getting openkb command: {e}")
        else:
            print("✗ CLI group doesn't have add_command method")

    else:
        print("✗ CLI group NOT found!")

except ImportError as e:
    print(f"✗ Failed to import cli.commands: {e}")
    print("\nTrying to import directly...")
    import importlib.util
    spec = importlib.util.spec_from_file_location("commands", str(Path(__file__).parent / "cli" / "commands.py"))
    if spec and spec.loader:
        commands = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(commands)
        print("✓ Successfully imported via direct module loading")
    else:
        print("✗ Direct module loading failed")

print("\n" + "=" * 60)
print("Test completed!")