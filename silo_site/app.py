#!/usr/bin/env python3
"""Standalone Flask release viewer for the experimental bulk data files."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
from threading import Lock
from typing import Any

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from flask import Flask, Response, abort, jsonify, redirect, send_file
import zstandard

ROOT_DIR = Path(__file__).resolve().parent.parent
SITE_DIR = Path(__file__).resolve().parent
STATIC_DIR = SITE_DIR / "static"
DATA_DIR = Path(os.environ.get("SILO_DATA_DIR", ROOT_DIR / "data")).resolve()
MANIFEST_PATH = DATA_DIR / "manifest.json"
S3_BUCKET = os.environ.get("SILO_S3_BUCKET")
TITLE = "NPD Local Bulk Data Viewer"
RESOURCE_ORDER = [
    "Practitioner",
    "PractitionerRole",
    "Organization",
    "Location",
    "Endpoint",
    "OrganizationAffiliation",
]

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _human_bytes(value: int | None) -> str | None:
    if value is None:
        return None

    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{value} B"


def _guess_release_date() -> str | None:
    newest_mtime = max(path.stat().st_mtime for path in DATA_DIR.iterdir() if path.is_file())
    return datetime.fromtimestamp(newest_mtime, tz=timezone.utc).date().isoformat()


def _resource_filename(resource_name: str) -> str:
    return f"{resource_name}.ndjson.zst"

def _get_resource_from_filename(filename: str) -> str:
    return filename.split("_")[0]

def _append_zst(filename: str) -> str:
    return filename + ".zst"


def _sort_keys_by_resource_order(keys: Iterable[str]) -> list[str]:
    return sorted(
        keys,
        key=lambda key: RESOURCE_ORDER.index(_get_resource_from_filename(key)),
    )

def _sample_fields(record: dict[str, Any]) -> dict[str, Any]:
    ordered_keys = [
        "resourceType",
        "id",
        "meta",
        "active",
        "status",
        "name",
        "description",
        "identifier",
        "telecom",
        "address",
        "position",
        "managingOrganization",
        "organization",
        "practitioner",
        "endpoint",
        "location",
        "specialty",
        "code",
    ]
    sampled = {key: record[key] for key in ordered_keys if key in record}
    if sampled:
        return sampled

    first_keys = list(record)[:8]
    return {key: record[key] for key in first_keys}


@dataclass(frozen=True)
class FileRecord:
    resource_name: str
    filename: str
    download_path: str
    compressed_bytes: int | None
    original_bytes: int | None
    compression_ratio_pct: float | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "resource_name": self.resource_name,
            "filename": self.filename,
            "download_path": self.download_path,
            "compressed_bytes": self.compressed_bytes,
            "compressed_size": _human_bytes(self.compressed_bytes),
            "original_bytes": self.original_bytes,
            "original_size": _human_bytes(self.original_bytes),
            "compression_ratio_pct": self.compression_ratio_pct,
            "sample_path": f"/api/samples/{self.resource_name}.json",
        }


class ReleaseStoreBase:
    def __init__(self) -> None:
        self._sample_cache: dict[str, list[dict[str, Any]]] = {}
        self._cache_lock = Lock()

    def manifest(self) -> dict[str, Any]:
        raise NotImplementedError

    def compressed_bytes(self, filename: str) -> int | None:
        raise NotImplementedError

    def release_date(self) -> str | None:
        raise NotImplementedError

    def samples(self, resource_name: str, count: int = 3) -> list[dict[str, Any]]:
        raise NotImplementedError

    def download_url(self, filename: str) -> str:
        raise NotImplementedError

    def files(self) -> list[FileRecord]:
        manifest = self.manifest()
        files_meta = manifest.get("files", {})
        records: list[FileRecord] = []
        for filename in _sort_keys_by_resource_order(files_meta.keys()):
            meta = files_meta.get(filename, {})
            resource_name = _get_resource_from_filename(filename)
            filename = _append_zst(filename)
            records.append(
                FileRecord(
                    resource_name=resource_name,
                    filename=filename,
                    download_path=f"/downloads/{filename}",
                    compressed_bytes=self.compressed_bytes(filename),
                    original_bytes=meta.get("original_bytes"),
                    compression_ratio_pct=meta.get("compression_ratio_pct"),
                )
            )

        records.append(
            FileRecord(
                resource_name="Manifest",
                filename="manifest.json",
                download_path="/downloads/manifest.json",
                compressed_bytes=self.compressed_bytes("manifest.json"),
                original_bytes=self.compressed_bytes("manifest.json"),
                compression_ratio_pct=None,
            )
        )
        return records

    def release_payload(self) -> dict[str, Any]:
        manifest = self.manifest()
        return {
            "title": TITLE,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "release_date": self.release_date(),
            "totals": {
                **manifest.get("totals", {}),
                "compressed_size": _human_bytes(manifest.get("totals", {}).get("compressed_bytes")),
                "original_size": _human_bytes(manifest.get("totals", {}).get("original_bytes")),
                "space_saved_size": _human_bytes(manifest.get("totals", {}).get("space_saved_bytes")),
            },
            "compression": {
                "algorithm": manifest.get("compression_algorithm"),
                "level": manifest.get("compression_level"),
            },
            "files": [record.to_dict() for record in self.files()],
            "notes": [
                "The bulk files are NDJSON compressed with zstd and are too large for spreadsheet tools.",
                "Sample records are read directly from the .zst archives.",
                "Windows: winget install Facebook.Zstandard",
                "macOS: brew install zstd",
                "Debian/Ubuntu: apt install zstd",
            ],
            "commands": [
                "zstdcat Practitioner.ndjson.zst | sed -n '1,2p'",
                "zstdcat Organization.ndjson.zst | jq -c '.identifier'",
                "zstdcat Location.ndjson.zst | rg 'SAN FRANCISCO|WILMINGTON'",
            ],
        }


class LocalReleaseStore(ReleaseStoreBase):
    def __init__(self) -> None:
        super().__init__()

    def manifest(self) -> dict[str, Any]:
        return _read_json(MANIFEST_PATH)

    def compressed_bytes(self, filename: str) -> int | None:
        path = DATA_DIR / filename
        return path.stat().st_size if path.exists() else None

    def release_date(self) -> str | None:
        return _guess_release_date()

    def samples(self, resource_name: str, count: int = 3) -> list[dict[str, Any]]:
        if resource_name not in RESOURCE_ORDER:
            raise FileNotFoundError(resource_name)

        with self._cache_lock:
            if resource_name in self._sample_cache:
                return self._sample_cache[resource_name]

        file_path = DATA_DIR / _resource_filename(resource_name)
        records: list[dict[str, Any]] = []
        dctx = zstandard.ZstdDecompressor()

        with file_path.open("rb") as source, dctx.stream_reader(source) as reader:
            text_reader = io.TextIOWrapper(reader, encoding="utf-8")
            for _ in range(count):
                line = text_reader.readline()
                if not line:
                    break
                records.append(_sample_fields(json.loads(line)))

        with self._cache_lock:
            self._sample_cache[resource_name] = records
        return records

    def download_url(self, filename: str) -> str:
        requested = (DATA_DIR / filename).resolve()
        if requested.parent != DATA_DIR.resolve() or not requested.exists():
            raise FileNotFoundError(filename)
        return str(requested)


class S3ReleaseStore(ReleaseStoreBase):
    def __init__(self, bucket: str) -> None:
        super().__init__()
        self.bucket = bucket
        self.client = boto3.client("s3", config=Config(signature_version="s3v4"))

    def manifest(self) -> dict[str, Any]:
        body = self.client.get_object(Bucket=self.bucket, Key="manifest.json")["Body"].read()
        return json.loads(body)

    def compressed_bytes(self, filename: str) -> int | None:
        try:
            return self.client.head_object(Bucket=self.bucket, Key=filename)["ContentLength"]
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") in {"404", "NoSuchKey"}:
                return None
            raise

    def release_date(self) -> str | None:
        timestamps = []
        for key in ["manifest.json", *[_resource_filename(name) for name in RESOURCE_ORDER]]:
            try:
                head = self.client.head_object(Bucket=self.bucket, Key=key)
            except ClientError:
                continue
            timestamps.append(head["LastModified"])
        if not timestamps:
            return None
        return max(timestamps).astimezone(timezone.utc).date().isoformat()

    def samples(self, resource_name: str, count: int = 3) -> list[dict[str, Any]]:
        if resource_name not in RESOURCE_ORDER:
            raise FileNotFoundError(resource_name)

        with self._cache_lock:
            if resource_name in self._sample_cache:
                return self._sample_cache[resource_name]

        key = _resource_filename(resource_name)
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        records: list[dict[str, Any]] = []
        dctx = zstandard.ZstdDecompressor()

        with dctx.stream_reader(response["Body"]) as reader:
            text_reader = io.TextIOWrapper(reader, encoding="utf-8")
            for _ in range(count):
                line = text_reader.readline()
                if not line:
                    break
                records.append(_sample_fields(json.loads(line)))

        with self._cache_lock:
            self._sample_cache[resource_name] = records
        return records

    def download_url(self, filename: str) -> str:
        try:
            return self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": filename},
                ExpiresIn=3600,
            )
        except ClientError as exc:
            raise FileNotFoundError(filename) from exc


STORE: ReleaseStoreBase = S3ReleaseStore(S3_BUCKET) if S3_BUCKET else LocalReleaseStore()


@app.get("/")
def index() -> Response:
    return send_file(STATIC_DIR / "index.html")


@app.get("/api/release.json")
def release() -> Response:
    return jsonify(STORE.release_payload())


@app.get("/api/samples/<resource_name>.json")
def samples(resource_name: str) -> Response:
    try:
        records = STORE.samples(resource_name)
        payload = {
            "resource_name": resource_name,
            "count": len(records),
            "records": records,
        }
    except FileNotFoundError:
        abort(404, description="Unknown resource")
    return jsonify(payload)


@app.get("/downloads/<path:filename>")
def download(filename: str) -> Response:
    try:
        target = STORE.download_url(filename)
    except FileNotFoundError:
        abort(404, description="Download not found")

    if isinstance(STORE, LocalReleaseStore):
        requested = Path(target)
        return send_file(requested, as_attachment=True, download_name=requested.name)

    return redirect(target, code=302)


def _validate_startup() -> None:
    if S3_BUCKET:
        try:
            STORE.manifest()
        except ClientError as exc:
            raise SystemExit(f"Unable to read manifest.json from s3://{S3_BUCKET}: {exc}") from exc
        return

    if not DATA_DIR.exists():
        raise SystemExit(f"Missing data directory: {DATA_DIR}")
    if not MANIFEST_PATH.exists():
        raise SystemExit(f"Missing manifest: {MANIFEST_PATH}")


def main() -> None:
    _validate_startup()
    app.run(host="127.0.0.1", port=8080, debug=False)


if __name__ == "__main__":
    main()