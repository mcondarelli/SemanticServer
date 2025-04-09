import sys
import subprocess
from pathlib import Path

BASE = Path(__file__).parent.parent
YAML = BASE / "openapi.yaml"
PYPROJECT = BASE / "pyproject.toml"
SETUP = BASE / "setup.py"
# sanity check
if not (PYPROJECT.exists() and YAML.exists() and SETUP.exists()):
    print(f'ERROR: "{__file__}" should be in "SmanticParser/scripts/"')
    sys,exit(1)

OUT = BASE / "src" / "semanticserver" / "models" / "generated.py"




print("🔧 Generating Pydantic models from OpenAPI spec...")
subprocess.run([
    "datamodel-codegen",
    "--input", str(YAML),
    "--input-file-type", "openapi",
    "--output", str(OUT)
], check=True)
