"""Run a request corpus against Django and FastAPI and compare responses."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

import requests
import yaml

from .diff import classify_response_pair
from .normalize import normalize_body, normalize_headers


def _read_corpus(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def _fetch(
    base_url: str,
    path: str,
    auth: tuple[str, str] | None,
    *,
    accept: str,
    local_netlocs: set[str],
    strip_local_trailing_slash: bool,
):
    response = requests.get(
        f"{base_url.rstrip('/')}{path}",
        auth=auth,
        headers={"Accept": accept},
        timeout=30,
    )
    return {
        "status": response.status_code,
        "headers": normalize_headers(dict(response.headers)),
        "raw_body": response.text,
        "body": normalize_body(
            response.headers.get("content-type"),
            response.text,
            local_netlocs=local_netlocs,
            strip_local_trailing_slash=strip_local_trailing_slash,
        ),
    }


def _parse_auth(username: str | None, password: str | None):
    if username and password:
        return (username, password)
    return None


def run_corpus(
    *,
    corpus_path: Path,
    django_base_url: str,
    fastapi_base_url: str,
    django_auth: tuple[str, str] | None = None,
    fastapi_auth: tuple[str, str] | None = None,
):
    corpus = _read_corpus(corpus_path)
    local_netlocs = {
        urlsplit(django_base_url).netloc,
        urlsplit(fastapi_base_url).netloc,
    }
    report = {
        "corpus": str(corpus_path),
        "resource": corpus.get("resource"),
        "cases": [],
    }
    failures = 0

    for case in corpus.get("cases", []):
        accept = case.get("accept", "application/fhir+json")
        strip_local_trailing_slash = case.get("strip_local_trailing_slash", True)
        django_result = _fetch(
            django_base_url,
            case["path"],
            django_auth,
            accept=accept,
            local_netlocs=local_netlocs,
            strip_local_trailing_slash=strip_local_trailing_slash,
        )
        fastapi_result = _fetch(
            fastapi_base_url,
            case["path"],
            fastapi_auth,
            accept=accept,
            local_netlocs=local_netlocs,
            strip_local_trailing_slash=strip_local_trailing_slash,
        )

        comparison = classify_response_pair(
            django_status=django_result["status"],
            fastapi_status=fastapi_result["status"],
            django_content_type=django_result["headers"].get("content-type"),
            fastapi_content_type=fastapi_result["headers"].get("content-type"),
            django_body=django_result["body"],
            fastapi_body=fastapi_result["body"],
        )

        case_report = {
            "name": case["name"],
            "path": case["path"],
            "strip_local_trailing_slash": strip_local_trailing_slash,
            "django": django_result,
            "fastapi": fastapi_result,
            "comparison": {
                "classification": comparison.classification,
                "status_match": comparison.status_match,
                "content_type_match": comparison.content_type_match,
                "body_match": comparison.body_match,
            },
        }
        report["cases"].append(case_report)
        if comparison.classification != "exact_match":
            failures += 1

    return report, failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare Django and FastAPI responses.")
    parser.add_argument("--corpus", required=True, type=Path)
    parser.add_argument("--django-base-url", required=True)
    parser.add_argument("--fastapi-base-url", required=True)
    parser.add_argument("--django-username")
    parser.add_argument("--django-password")
    parser.add_argument("--fastapi-username")
    parser.add_argument("--fastapi-password")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    django_auth = _parse_auth(args.django_username, args.django_password)
    fastapi_auth = _parse_auth(args.fastapi_username, args.fastapi_password)
    report, failures = run_corpus(
        corpus_path=args.corpus,
        django_base_url=args.django_base_url,
        fastapi_base_url=args.fastapi_base_url,
        django_auth=django_auth,
        fastapi_auth=fastapi_auth,
    )

    if args.output:
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True))

    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
