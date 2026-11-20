#!/usr/bin/env python3
"""Entry program for news-image-20261119 (make.fun).

The artwork is pre-rendered next to this file as entry.png (see draw.py for
the generator and README.md for sources). This program's whole job is to
place that image at the output location the grader expects, using only the
Python standard library, with no network access. It is deterministic: the
output bytes are exactly the committed entry.png bytes on every run.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")


def target_path():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    return os.path.join(out_dir, "entry.png")


def main():
    dest = target_path()
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copyfile(SOURCE, dest)
    print(f"entry.png -> {dest} ({os.path.getsize(dest)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
