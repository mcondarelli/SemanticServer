#!/usr/bin/bash
set -ex

script_path=$(readlink -f "$0" 2>/dev/null || realpath "$0" 2>/dev/null || echo "$0")
sdir="$(dirname "${script_path}")"
here="$(cd "$sdir" && pwd)"

root="$(dirname "${here}")"
cd $root

YAML="$root/openapi.yaml"
PYPROG="$root/pyproject.xml"
SETUP="$root/setup.py"
OUT="$root/src/semanticserver/models/generated.py"
# Sanity check
[ -f "$root/openapi.yaml" -a -f "$root/pyproject.toml" -a -f "$root/setup.py" ] \
    || (echo "ERROR '$script_path' should be in SemanticParser/scripts/"; exit 1)
VENV="$root/.venv"

python3 -m venv "$VENV"
source "$VENV/bin/activate"

pip install -e .[dev]
python scripts/bootstrap.py

if [ 'rocm' == "$1" ]
then
    pip uninstall -y torch torchvision torchaudio sentence-transformers

    # Install ROCm-compatible stack
    pip install --pre torch \
      --index-url https://download.pytorch.org/whl/nightly/rocm6.3

    # Then re-install sentence-transformers *without* triggering torch reinstallation
    pip install sentence-transformers --no-deps
    pip install -e .[dev]  # now safe
fi

echo "🔧 Generating Pydantic models from OpenAPI spec..."
datamodel-codegen --input "$YAML" --input-file-type  openapi --output "$OUT"

