#!/usr/bin/env python3
"""Phase 1 setup: check Ollama is installed, then pull configured models."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MODELS_YAML = ROOT / "configs" / "models.yaml"


def check_ollama() -> str:
    path = shutil.which("ollama")
    if not path:
        print("Ollama is not installed (or not on your PATH).")
        print()
        print("Install it, then re-run this script:")
        print("  https://ollama.com/download")
        print("  # or: brew install ollama")
        print()
        print("After install, start the app once so the Ollama server is running.")
        sys.exit(1)

    result = subprocess.run(
        ["ollama", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    version = (result.stdout or result.stderr or "").strip() or "unknown"
    print(f"Ollama found: {path}")
    print(f"Version: {version}")
    return path


def load_model_names() -> list[str]:
    data = yaml.safe_load(MODELS_YAML.read_text(encoding="utf-8"))
    return [str(m["name"]) for m in data["models"]]


def pull_models(names: list[str]) -> None:
    print()
    print(f"Pulling {len(names)} model(s). This needs network once; then you can go offline.")
    for name in names:
        print(f"\n=== ollama pull {name} ===")
        result = subprocess.run(["ollama", "pull", name], check=False)
        if result.returncode != 0:
            print(f"Failed to pull {name} (exit {result.returncode}).")
            print("Check the tag at https://ollama.com/library and update configs/models.yaml.")
            sys.exit(result.returncode)
    print("\nAll models pulled.")


def main() -> None:
    check_ollama()
    names = load_model_names()
    print(f"Models from {MODELS_YAML.relative_to(ROOT)}: {', '.join(names)}")
    pull_models(names)
    print()
    print("Next:")
    print("  uv sync")
    print("  uv run assistant chat")


if __name__ == "__main__":
    main()
