#!/usr/bin/env bash
# =============================================================================
# setup_env.sh  —  Project environment setup for VS Code / Jupyter
#
# Usage:
#   chmod +x setup_env.sh
#   ./setup_env.sh
#
# What it does:
#   1. Creates a Python virtual environment in .venv/
#   2. Installs all dependencies from requirements.txt
#   3. Registers the venv as a Jupyter kernel named "her2-analysis"
#      (this is what VS Code will list in the kernel picker)
#   4. Prints next steps for VS Code
# =============================================================================

set -euo pipefail

VENV_DIR=".venv"
KERNEL_NAME="her2-analysis"
KERNEL_DISPLAY="HER2 Analysis (Python 3)"
PYTHON_BIN="python3"

# --------------------------------------------------------------------------- #
# 1. Create virtual environment
# --------------------------------------------------------------------------- #
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Step 1/4 — Creating virtual environment in .venv/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "$VENV_DIR" ]; then
    echo "  ⚠  .venv/ already exists — skipping creation."
else
    $PYTHON_BIN -m venv "$VENV_DIR"
    echo "  ✓  Virtual environment created."
fi

# --------------------------------------------------------------------------- #
# 2. Activate and upgrade pip
# --------------------------------------------------------------------------- #
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Step 2/4 — Upgrading pip"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

source "$VENV_DIR/bin/activate"
pip install --upgrade pip --quiet
echo "  ✓  pip upgraded to $(pip --version | awk '{print $2}')"

# --------------------------------------------------------------------------- #
# 3. Install dependencies
# --------------------------------------------------------------------------- #
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Step 3/4 — Installing dependencies from requirements.txt"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

pip install -r requirements.txt --quiet
echo "  ✓  All packages installed."

# --------------------------------------------------------------------------- #
# 4. Register Jupyter kernel for VS Code
# --------------------------------------------------------------------------- #
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Step 4/4 — Registering Jupyter kernel: '$KERNEL_DISPLAY'"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python -m ipykernel install --user \
    --name "$KERNEL_NAME" \
    --display-name "$KERNEL_DISPLAY"
echo "  ✓  Kernel registered."

# --------------------------------------------------------------------------- #
# Done — print VS Code instructions
# --------------------------------------------------------------------------- #
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅  Setup complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Next steps in VS Code:"
echo ""
echo "  1. Open this project folder in VS Code:"
echo "       File → Open Folder → $(pwd)"
echo ""
echo "  2. Open any notebook in notebooks/"
echo ""
echo "  3. Click 'Select Kernel' (top right of the notebook)"
echo "       → Choose: '$KERNEL_DISPLAY'"
echo ""
echo "  4. To activate the venv in a terminal:"
echo "       source .venv/bin/activate"
echo ""
echo "  Kernel location:"
python -m jupyter kernelspec list | grep "$KERNEL_NAME" || true
echo ""
