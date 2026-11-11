"""Run the conversational agent acceptance checks from the repository root."""
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
runpy.run_path(str(ROOT / "tests" / "test_agent.py"), run_name="__main__")
