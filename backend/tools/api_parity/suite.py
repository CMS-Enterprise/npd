"""Run every parity corpus and emit a single summary report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .runner import _parse_auth, run_corpus


def _default_corpora_dir() -> Path:
    return Path(__file__).resolve().parent / "corpus"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run all API parity corpora.")
    parser.add_argument("--corpora-dir", type=Path, default=_default_corpora_dir())
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

    corpora = sorted(args.corpora_dir.glob("*.yaml"))
    suite_report = {
        "django_base_url": args.django_base_url,
        "fastapi_base_url": args.fastapi_base_url,
        "corpora": [],
        "summary": {
            "corpora_total": len(corpora),
            "corpora_with_failures": 0,
            "cases_total": 0,
            "cases_failed": 0,
        },
    }

    for corpus_path in corpora:
        report, failures = run_corpus(
            corpus_path=corpus_path,
            django_base_url=args.django_base_url,
            fastapi_base_url=args.fastapi_base_url,
            django_auth=django_auth,
            fastapi_auth=fastapi_auth,
        )
        case_total = len(report["cases"])
        suite_report["corpora"].append(
            {
                "corpus": str(corpus_path),
                "resource": report.get("resource"),
                "case_total": case_total,
                "failures": failures,
                "status": "pass" if failures == 0 else "fail",
            }
        )
        suite_report["summary"]["cases_total"] += case_total
        suite_report["summary"]["cases_failed"] += failures
        if failures:
            suite_report["summary"]["corpora_with_failures"] += 1

    if args.output:
        args.output.write_text(json.dumps(suite_report, indent=2, sort_keys=True))

    print(json.dumps(suite_report, indent=2, sort_keys=True))
    return 1 if suite_report["summary"]["cases_failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
