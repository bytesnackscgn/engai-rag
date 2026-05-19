# Setup Guide - KfW Energieberater Assistent

## Prerequisites

- Python 3.10+
- pip (Python package manager)

## Quick Start

### Option 1: Full Setup with Virtual Environment (Recommended for Development)

```bash
# Run the setup script
./setup_venv.sh

# Activate the virtual environment
source venv/bin/activate

# Install the CLI
pip3 install -e .

# Test it
engaichat status
```

### Option 2: Quick Install (Global, NOT recommended)

```bash
# One-command installation (no virtual environment)
./setup.sh

# Test it
engaichat status
```

## Installation Options

### Recommended: Virtual Environment

**Why use venv?**
- ✅ Isolated dependencies - doesn't affect system Python
- ✅ Safe to delete and recreate
- ✅ Multiple projects can coexist
- ✅ Reproducible environments

**How to use:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
# On Windows: venv\Scripts\activate

# Install dependencies
pip3 install -r requirements.txt

# Install CLI
pip3 install -e .

# Deactivate when done
deactivate
```

### Quick Test: No Virtual Environment

**Why use global install?**
- ✅ Quick for testing
- ✅ No setup overhead

**When NOT to use:**
- ❌ Development (can break system Python)
- ❌ Multiple Python projects
- ❌ Production deployments

**How to use:**
```bash
# Install globally (careful!)
pip3 install -r requirements.txt
pip3 install -e .

# Test
engaichat status

# Uninstall to revert
pip uninstall -y engaichat
pip uninstall -y openkb fastapi uvicorn click loguru
```

## Configuration

### 1. Set API Keys

```bash
# Copy the template
cp .env.example .env

# Edit with your API keys
nano .env
```

Required variables:
```bash
OPENROUTER_API_KEY=your_openrouter_api_key_here
API_KEY=your_secure_api_key_here
```

### 2. OpenKB Configuration

Already configured in `.openkb/config.yaml`:
```yaml
model: z-ai/glm-4.7-flash
language: de
pageindex_threshold: 20
```

## Directory Structure

After setup, you'll have:

```
engai-rag/
├── venv/                    # Virtual environment
├── cache/                   # Caches
│   └── query_cache/
├── logs/                    # Log files
├── raw/                     # Document repository
│   ├── kfws/
│   ├── sanierung/
│   ├── berechnungen/
│   └── muster/
├── wiki/                    # Generated wiki
│   ├── index.md
│   ├── concepts/
│   ├── summaries/
│   └── sources/
├── .env                     # Environment variables
├── .env.example             # Configuration template
└── .openkb/                 # OpenKB config
    └── config.yaml
```

## Verifying Installation

### Check Python
```bash
python --version
# Should be 3.10+
```

### Check CLI
```bash
engaichat status
engaichat check
engaichat validate
```

### Check Packages
```bash
python -c "import openkb; print('OpenKB:', openkb.__version__)"
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
python -c "from cli.commands import cli; print('CLI OK')"
```

## Common Issues

### Virtual Environment Not Activating
```bash
# Check if exists
ls -la venv/bin/activate

# Recreate if needed
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

### Package Installation Fails
```bash
# Check Python version
python --version

# Clear pip cache
pip cache purge

# Install specific package
pip install openkb==0.2.0

# Try again
pip install -r requirements.txt
```

### .env File Missing
```bash
# Create from template
cp .env.example .env

# Add your API keys
nano .env
```

### CLI Commands Not Found
```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall CLI
pip install -e .

# Test again
engaichat --help
```

## Next Steps

1. **Add Documents**
   ```bash
   # Place your KfW documents in raw/ directory
   mkdir -p raw/kfws
   # Copy your documents here
   ```

2. **Start Server**
   ```bash
   # Activate venv
   source venv/bin/activate

   # Start server
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Test API**
   ```bash
   # Health check
   curl http://localhost:8000/api/health

   # Test chat endpoint
   curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your_api_key" \
     -d '{"message": "Test message"}'
   ```

## Development Workflow

```bash
# 1. Start server in one terminal
source venv/bin/activate
uvicorn api.main:app --reload

# 2. Test in another terminal
source venv/bin/activate
engaichat status

# 3. Check API docs
# Open browser to: http://localhost:8000/docs
```

## Cleanup

### Remove Virtual Environment
```bash
# Deactivate first
deactivate

# Delete venv directory
rm -rf venv
```

### Reinstall from Scratch
```bash
# Remove everything
rm -rf venv cache logs

# Reinstall
./setup_venv.sh
source venv/bin/activate
pip install -e .
```