#!/usr/bin/env python3
"""Compatibility wrapper for the renamed production handoff bundle builder."""

from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    target = Path(__file__).with_name("build_generation_handoff_bundle.py")
    runpy.run_path(str(target), run_name="__main__")
