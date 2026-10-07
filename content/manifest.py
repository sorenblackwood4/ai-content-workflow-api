"""Create a reviewable, offline content-generation handoff."""
from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

KINDS = ("text", "image", "video")
LEDGER_FIELDS = ("step_id", "kind", "model", "status", "request_id", "output_path", "estimated_usd", "error_class", "recorded_at")


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return cleaned[:80] or "untitled"


def build(topic: str, *, folder: str = "output", text_model: str = "gpt-5.4", image_model: str = "gpt-image-2", video_model: str = "seedance-2.5") -> dict[str, Any]:
    if not topic.strip():
        raise ValueError("topic must not be empty")
    if not folder.strip() or Path(folder).is_absolute():
        raise ValueError("folder must be a relative output directory")
    models = {"text": text_model, "image": image_model, "video": video_model}
    if not all(isinstance(value, str) and value.strip() for value in models.values()):
        raise ValueError("all model IDs must be non-empty")
    steps = [
        {"step_id": "text-01", "kind": "text", "model": text_model, "depends_on": [], "output_path": "text/brief.md", "approval_required": True},
        {"step_id": "image-01", "kind": "image", "model": image_model, "depends_on": ["text-01"], "output_path": "image/cover.png", "approval_required": True},
        {"step_id": "video-01", "kind": "video", "model": video_model, "depends_on": ["text-01", "image-01"], "output_path": "video/clip.mp4", "approval_required": True},
    ]
    return {"schema": 1, "topic": topic.strip(), "slug": _slug(topic), "folder": folder, "created_at": datetime.now(timezone.utc).isoformat(), "base_url": "https://argolink.io/v1", "steps": steps}


def write_ledger(path: Path, rows: list[dict[str, Any]] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=LEDGER_FIELDS)
        writer.writeheader()
        for row in rows or []:
            writer.writerow({field: row.get(field, "") for field in LEDGER_FIELDS})


def create_run(topic: str, *, root: str | Path = "output", **models: str) -> Path:
    # Keep the manifest's logical folder portable while allowing the caller to
    # choose an absolute temporary/output root on the local filesystem.
    manifest = build(topic, folder="output", **models)
    manifest["folder"] = str(root)
    run_dir = Path(root) / manifest["slug"]
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_ledger(run_dir / "steps.csv")
    for step in manifest["steps"]:
        (run_dir / Path(step["output_path"]).parent).mkdir(parents=True, exist_ok=True)
    return run_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an offline text/image/video handoff")
    parser.add_argument("topic")
    parser.add_argument("--out", default="output")
    args = parser.parse_args()
    run_dir = create_run(args.topic, root=args.out)
    print(run_dir)


if __name__ == "__main__":
    main()
