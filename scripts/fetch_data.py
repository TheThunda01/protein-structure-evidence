"""Retrieve pinned public source bytes; refuse unreviewed source changes."""

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
from urllib.request import urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir",type=Path,default=Path("data"))
    args=parser.parse_args()
    manifest=json.loads((args.data_dir/"provenance.json").read_text())
    with tempfile.TemporaryDirectory(prefix="protein_sources_") as tmp:
        staging=Path(tmp)
        for item in manifest["files"]:
            with urlopen(item["source_url"],timeout=45) as response:
                data=response.read()
            if item["normalization"]=="json-indent-2":
                data=json.dumps(json.loads(data),indent=2).encode("utf-8")
            if len(data)!=item["bytes"] or hashlib.sha256(data).hexdigest()!=item["sha256"]:
                raise SystemExit(f"Source changed: {item['path']}. No source files replaced; review the new version before repinning.")
            (staging/item["path"]).write_bytes(data)
        for item in manifest["files"]:
            (args.data_dir/item["path"]).write_bytes((staging/item["path"]).read_bytes())
    print(f"Verified and restored {len(manifest['files'])} pinned source files")


if __name__=="__main__":
    main()
