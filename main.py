# news-image-20261125 — acct3 entrypoint.
# Writes the day's newspaper image to /output/entry.png. Deterministic, no network.
import os
import shutil

from build import build


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    target = os.path.join(out, "entry.png")
    build(target)
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    if os.path.abspath(target) != os.path.abspath(here):
        shutil.copyfile(target, here)


if __name__ == "__main__":
    main()
