# news-image-20261125 — acct3 entrypoint.
# Copies the pre-built entry.png to the output directory, byte-identical.
# Standard library only; no network, no randomness, no PIL, no fonts.
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    shutil.copyfile(SRC, os.path.join(out, "entry.png"))


if __name__ == "__main__":
    main()
