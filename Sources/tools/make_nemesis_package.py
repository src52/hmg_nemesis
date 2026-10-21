#!/usr/bin/env python3
"""Build a reproducible NEMESIS install zip from a package directory."""
from __future__ import annotations

import argparse
import stat
import zipfile
from pathlib import Path


ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pkg_dir", type=Path)
    ap.add_argument("-o", "--output", type=Path, default=None)
    args = ap.parse_args()
    src = args.pkg_dir.resolve()
    meta = src / "NEMESIS.data"
    if not meta.is_file():
        raise SystemExit(f"missing {meta}")
    out = args.output or (src.parent / f"{src.name}.zip")
    with zipfile.ZipFile(
        out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as z:
        for p in sorted(src.rglob("*")):
            if p.is_file():
                name = p.relative_to(src).as_posix()
                info = zipfile.ZipInfo(name, date_time=ZIP_EPOCH)
                info.create_system = 3
                info.external_attr = (stat.S_IMODE(p.stat().st_mode) & 0xFFFF) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, p.read_bytes())
    print(f"Wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
