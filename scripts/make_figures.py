"""python scripts/make_figures.py NAME [NAME ...] [--graph PATH] [--out-dir DIR]   (NAME: f, ..., all)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from routing.figures import main

if __name__ == "__main__":
    main()

