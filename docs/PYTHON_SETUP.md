# Python Environment Setup

CodeSwarm requires Python 3.11. This guide shows you how to set up a virtual environment for safe, isolated dependency management.

## Why Use a Virtual Environment?

✅ **Isolation**: Dependencies don't conflict with system Python
✅ **Reproducibility**: Same environment across machines
✅ **Safety**: Won't break system Python packages
✅ **Convenience**: Just type `python` instead of `python3.11`
✅ **Best Practice**: Industry standard for Python projects

## Quick Start

```bash
# 1. Navigate to CodeSwarm directory
cd /path/to/codeswarm

# 2. Create virtual environment with Python 3.11
python3.11 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run CodeSwarm (now you can just use 'python')
python codeswarm.py --task "your task here"
```

## Step-by-Step Setup

### 1. Verify Python 3.11 is Installed

```bash
python3.11 --version
```

If you don't have Python 3.11:
```bash
# macOS (using Homebrew)
brew install python@3.11

# Linux (Ubuntu/Debian)
sudo apt-get install python3.11 python3.11-venv

# Or use pyenv (see Alternative Setup below)
```

### 2. Create Virtual Environment

```bash
# In the codeswarm directory
python3.11 -m venv venv
```

This creates a `venv/` folder containing an isolated Python 3.11 environment.

### 3. Activate Virtual Environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

You'll see `(venv)` in your terminal prompt when activated:
```
(venv) user@computer:~/codeswarm$
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Verify Installation

```bash
python --version  # Should show Python 3.11.x
which python      # Should point to venv/bin/python
```

### 6. Run CodeSwarm

```bash
# Now you can use 'python' instead of 'python3.11'
python codeswarm.py --task "create a landing page"
```

## Deactivating the Virtual Environment

When you're done working:
```bash
deactivate
```

The `(venv)` prefix will disappear from your prompt.

## Auto-Activation (Optional)

### Option 1: Using direnv (Recommended)

Automatically activate the virtual environment when you `cd` into the project:

```bash
# 1. Install direnv
brew install direnv  # macOS
# or
sudo apt-get install direnv  # Linux

# 2. Add to your shell profile (~/.zshrc or ~/.bashrc)
eval "$(direnv hook zsh)"  # or bash

# 3. Create .envrc in codeswarm directory
echo "source venv/bin/activate" > .envrc

# 4. Allow direnv to run
direnv allow

# 5. Now it auto-activates when you cd into the directory!
```

### Option 2: Shell Alias

Add to your `~/.zshrc` or `~/.bashrc`:
```bash
alias codeswarm='cd /path/to/codeswarm && source venv/bin/activate'
```

Then just run:
```bash
codeswarm  # Auto-navigates and activates venv
python codeswarm.py --task "your task"
```

### Option 3: Startup Script

Create a `run.sh` script:
```bash
#!/bin/bash
# Activate venv and run CodeSwarm
source venv/bin/activate
python codeswarm.py "$@"
```

Make it executable:
```bash
chmod +x run.sh
```

Usage:
```bash
./run.sh --task "create a portfolio website"
```

## Alternative Setup: Using pyenv

For more sophisticated Python version management:

```bash
# 1. Install pyenv
brew install pyenv  # macOS
# or follow: https://github.com/pyenv/pyenv#installation

# 2. Install Python 3.11
pyenv install 3.11.9

# 3. Set as local version for this directory
cd /path/to/codeswarm
pyenv local 3.11.9

# 4. Create virtual environment
python -m venv venv

# 5. Activate and continue as normal
source venv/bin/activate
pip install -r requirements.txt
```

## Troubleshooting

### "python3.11: command not found"

Install Python 3.11:
```bash
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv

# Or use pyenv (see above)
```

### "No module named 'xyz'"

Make sure the virtual environment is activated:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Virtual environment not activating

Check that `venv/bin/activate` exists:
```bash
ls -la venv/bin/activate
```

If it doesn't exist, recreate the virtual environment:
```bash
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Wrong Python version in venv

Recreate with explicit Python 3.11:
```bash
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
python --version  # Verify it's 3.11.x
```

## Managing Dependencies

### Adding New Dependencies

```bash
# Activate venv first
source venv/bin/activate

# Install package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt
```

### Updating Dependencies

```bash
# Activate venv
source venv/bin/activate

# Update all packages
pip install --upgrade -r requirements.txt

# Or update specific package
pip install --upgrade package-name
```

## Best Practices

1. **Always activate venv** before running CodeSwarm
2. **Never commit venv/** to git (already in `.gitignore`)
3. **Keep requirements.txt updated** when adding packages
4. **Use `pip freeze`** to capture exact versions for reproducibility
5. **Deactivate when done** to avoid confusion with other projects

## Next Steps

Once your environment is set up, see:
- [Installation Guide](../README.md#installation) - Configure API keys and services
- [Usage Guide](../README.md#usage) - Start generating code
- [Configuration Guide](CONFIGURATION.md) - Advanced settings
