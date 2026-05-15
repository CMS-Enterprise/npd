#!/usr/bin/env python3
"""
Normalize identity-provider records into a common practitioner identity shape,
resolve the best-matching practitioner/NPI from CoreDM, and return an expanded
profile assembled from multiple CoreDM tables.

Typical usage:

```
python3 backend/practitioner_identity_lookup.py --env-file backend/examples/.env --provider id.me --json-file backend/examples/id_me_veronica_example.json
```
OR
```
python3 backend/practitioner_identity_lookup.py \
 --provider login.gov \
 --json-text '{"sub":"abc","given_name":"Jane","family_name":"Doe","birthdate":"1980-01-15"}' \
 --env-file backend/examples/.env
```
OR
```
cat backend/examples/id_me_veronica_example.json | \
python3 backend/practitioner_identity_lookup.py \
 --provider id.me \
 --env-file backend/examples/.env
```
OR
python3 backend/practitioner_identity_lookup.py --env-file backend/examples/.env  --id-me-file backend/examples/id_me_veronica_example.json

All three
```
python3 backend/practitioner_identity_lookup.py --env-file backend/examples/.env  --id-me-file backend/examples/id_me_veronica_example.json --clear-me-file backend/examples/clear_me_veronica_example.json --login-gov-file backend/examples/login_gov_veronica_example.json
```
Or two
```
python3 backend/practitioner_identity_lookup.py --env-file backend/examples/.env  --id-me-file backend/examples/id_me_veronica_example.json --clear-me-file backend/examples/clear_me_veronica_example.json
```

Assumptions:
- We are matching against the CoreDM schema, defaulting to `core_data_model`.
- The strongest keys are NPI, exact DOB, exact name, state license, and phone.
- Email is normalized from incoming records but CoreDM currently has no canonical
  practitioner email table, so it is not used for matching yet.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path
import argparse
import json
import os
import re
from typing import Any, Iterable, Mapping, Sequence

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL


ProviderName = str

MATCH_WEIGHT_NPI_EXACT = 100
MATCH_WEIGHT_SSN_EXACT = 95
MATCH_WEIGHT_SSN_LAST4 = 18
MATCH_WEIGHT_NAME_EXACT = 35
MATCH_WEIGHT_MIDDLE_NAME_EXACT = 10
MATCH_WEIGHT_DOB_EXACT = 25
MATCH_WEIGHT_PHONE_EXACT = 12
MATCH_WEIGHT_STATE_LICENSE_EXACT = 20

MATCH_WEIGHT_SUMMARY: dict[str, int] = {
    "npi_exact": MATCH_WEIGHT_NPI_EXACT,
    "ssn_exact": MATCH_WEIGHT_SSN_EXACT,
    "ssn_last4": MATCH_WEIGHT_SSN_LAST4,
    "name_exact": MATCH_WEIGHT_NAME_EXACT,
    "middle_name_exact": MATCH_WEIGHT_MIDDLE_NAME_EXACT,
    "dob_exact": MATCH_WEIGHT_DOB_EXACT,
    "phone_exact": MATCH_WEIGHT_PHONE_EXACT,
    "state_license_exact": MATCH_WEIGHT_STATE_LICENSE_EXACT,
}

MAX_MATCH_SCORE = sum(MATCH_WEIGHT_SUMMARY.values())

MERGE_PROVIDER_PRIORITY: tuple[ProviderName, ...] = (
    "id.me",
    "login.gov",
    "clear.me",
)


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)


def _load_env_files(paths: Sequence[Path]) -> None:
    for path in paths:
        _load_env_file(path)


def _env(name: str, *fallback: str, default: str | None = None) -> str | None:
    if os.getenv(name):
        return os.getenv(name)
    for alt in fallback:
        if os.getenv(alt):
            return os.getenv(alt)
    return default


def _build_db_url() -> URL:
    db_host = _env("DB_HOST")
    db_port = int(_env("DB_PORT"))
    db_name = _env("DB_NAME")
    db_user = _env("DB_USER")
    db_password = _env("DB_PASSWORD")
    db_sslmode = _env("DB_SSLMODE")
    db_gssencmode = _env("DB_GSSENCMODE", default="disable")
    db_connect_timeout = int(_env("DB_CONNECT_TIMEOUT", default="5"))

    missing = [
        key
        for key, value in (
            ("DB_HOST", db_host),
            ("DB_NAME", db_name),
            ("DB_USER", db_user),
            ("DB_PASSWORD", db_password),
        )
        if not value
    ]
    if missing:
        raise ValueError(
            "Missing DB configuration for practitioner lookup: "
            + ", ".join(missing)
        )

    return URL.create(
        "postgresql+psycopg2",
        username=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        database=db_name,
        query={
            "sslmode": str(db_sslmode),
            "gssencmode": str(db_gssencmode),
            "connect_timeout": str(db_connect_timeout),
        },
    )


def _get_path(data: Mapping[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return None
        current = current[part]
    return current


def _first_present(data: Mapping[str, Any], aliases: Iterable[str]) -> Any:
    for alias in aliases:
        value = _get_path(data, alias) if "." in alias else data.get(alias)
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None


def _string_or_none(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return str(value)


def _bool_or_none(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text_value = _string_or_none(value)
    if text_value is None:
        return None
    lowered = text_value.lower()
    if lowered in {"true", "t", "1", "yes", "y"}:
        return True
    if lowered in {"false", "f", "0", "no", "n"}:
        return False
    return None


def _parse_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    text_value = _string_or_none(value)
    if text_value is None:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(text_value, fmt).date()
        except ValueError:
            continue
    return None


def _digits_only(value: str | None) -> str | None:
    if not value:
        return None
    digits = re.sub(r"\D+", "", value)
    return digits or None


def _normalize_npi(value: Any) -> int | None:
    text_value = _digits_only(_string_or_none(value))
    if not text_value:
        return None
    if len(text_value) != 10:
        return None
    return int(text_value)


def _normalize_name(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(value.strip().split())
    return cleaned or None


def _pick_joined_name(*parts: str | None) -> str | None:
    joined = " ".join(part for part in parts if part)
    return _normalize_name(joined)


@dataclass(frozen=True)
class CommonIdentityRecord:
    source: ProviderName
    raw_record: dict[str, Any]
    subject_id: str | None = None
    npi: int | None = None
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    name_suffix: str | None = None
    full_name: str | None = None
    ssn: str | None = None
    ssn_last4: str | None = None
    email: str | None = None
    email_verified: bool | None = None
    phone: str | None = None
    phone_verified: bool | None = None
    date_of_birth: date | None = None
    state_license_number: str | None = None
    state_license_state: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    address_city: str | None = None
    address_state: str | None = None
    address_postal_code: str | None = None
    address_country: str | None = None

    @property
    def phone_digits(self) -> str | None:
        return _digits_only(self.phone)

    @property
    def ssn_digits(self) -> str | None:
        return _digits_only(self.ssn)

    @property
    def ssn_last4_digits(self) -> str | None:
        return _digits_only(self.ssn_last4)

    @property
    def first_name_normalized(self) -> str | None:
        return _normalize_name(self.first_name)

    @property
    def middle_name_normalized(self) -> str | None:
        return _normalize_name(self.middle_name)

    @property
    def last_name_normalized(self) -> str | None:
        return _normalize_name(self.last_name)


@dataclass(frozen=True)
class PractitionerMatchCandidate:
    practitioner_id: str
    npi_id: int | None
    matched_name: str | None
    date_of_birth: date | None
    state_license_number: str | None
    state_license_state: str | None
    score: int
    score_breakdown: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PractitionerResolution:
    identity: CommonIdentityRecord
    matched_candidate: PractitionerMatchCandidate
    profile: dict[str, Any]
    source_identities: list[CommonIdentityRecord] = field(default_factory=list)
    identity_bundle_summary: dict[str, Any] = field(default_factory=dict)


class PractitionerMatchError(RuntimeError):
    pass


class PractitionerIdentityLookup:
    """
    One-stop abstraction for:
    1. normalizing `id.me`, `clear.me`, and `login.gov` records
    2. matching them to a CoreDM practitioner / NPI
    3. returning a joined practitioner profile
    """

    _ALIASES: dict[str, dict[str, tuple[str, ...]]] = {
        "id.me": {
            "subject_id": ("sub", "id", "uuid", "user_id", "user_uuid"),
            "npi": ("npi", "provider_npi", "provider.npi"),
            "first_name": ("fname", "first_name", "firstName", "given_name", "name.first"),
            "middle_name": ("mname", "middle_name", "middleName", "name.middle"),
            "last_name": ("lname", "last_name", "lastName", "family_name", "name.last"),
            "name_suffix": ("suffix", "name_suffix", "name.suffix"),
            "full_name": ("name", "full_name", "display_name"),
            "ssn": ("ssn",),
            "ssn_last4": ("ssn_last4",),
            "email": ("email", "email_address"),
            "email_verified": ("email_verified",),
            "phone": ("phone", "phone_number", "mobile_phone"),
            "phone_verified": ("phone_verified",),
            "date_of_birth": ("dob", "date_of_birth", "birthdate"),
            "state_license_number": ("license_number", "state_license_number"),
            "state_license_state": ("license_state", "state_license_state"),
            "address_line_1": ("address.street", "address_line_1", "primary_address.street1"),
            "address_line_2": ("address.street2", "address_line_2", "primary_address.street2"),
            "address_city": ("address.city", "city", "primary_address.city"),
            "address_state": ("address.state", "state", "primary_address.state"),
            "address_postal_code": ("address.zip", "address.postal_code", "zip", "primary_address.postal_code"),
            "address_country": ("address.country", "country", "primary_address.country"),
        },
        "clear.me": {
            "subject_id": ("sub", "subject", "clear_id", "person_id", "person.id"),
            "npi": ("npi", "provider_npi", "provider.npi"),
            "first_name": ("given_name", "first_name", "person.first_name", "person.given_name"),
            "middle_name": ("middle_name", "person.middle_name"),
            "last_name": ("family_name", "last_name", "person.last_name", "person.family_name"),
            "name_suffix": ("suffix", "person.suffix"),
            "full_name": ("name", "full_name", "person.full_name"),
            "ssn": ("ssn", "person.ssn"),
            "ssn_last4": ("ssn_last4", "person.ssn_last4"),
            "email": ("email", "person.email"),
            "email_verified": ("email_verified", "person.email_verified"),
            "phone": ("phone", "phone_number", "person.phone"),
            "phone_verified": ("phone_verified", "person.phone_verified"),
            "date_of_birth": ("birthdate", "dob", "person.birthdate"),
            "state_license_number": ("license_number", "state_license_number"),
            "state_license_state": ("license_state", "state_license_state"),
            "address_line_1": ("address.line1", "person.address.line1"),
            "address_line_2": ("address.line2", "person.address.line2"),
            "address_city": ("address.city", "person.address.city"),
            "address_state": ("address.state", "person.address.state"),
            "address_postal_code": ("address.postal_code", "address.zip", "person.address.postal_code"),
            "address_country": ("address.country", "person.address.country"),
        },
        "login.gov": {
            "subject_id": ("sub",),
            "npi": ("npi", "provider_npi"),
            "first_name": ("given_name", "first_name"),
            "middle_name": ("middle_name",),
            "last_name": ("family_name", "last_name"),
            "name_suffix": ("name_suffix", "suffix"),
            "full_name": ("name",),
            "ssn": ("ssn",),
            "ssn_last4": ("ssn_last4",),
            "email": ("email",),
            "email_verified": ("email_verified",),
            "phone": ("phone_number", "phone"),
            "phone_verified": ("phone_verified",),
            "date_of_birth": ("birthdate", "date_of_birth"),
            "state_license_number": ("license_number", "state_license_number"),
            "state_license_state": ("license_state", "state_license_state"),
            "address_line_1": ("address.street_address", "address_line_1"),
            "address_line_2": ("address.street_address_2", "address_line_2"),
            "address_city": ("address.locality", "address.city"),
            "address_state": ("address.region", "address.state"),
            "address_postal_code": ("address.postal_code", "address.zip"),
            "address_country": ("address.country",),
        },
    }

    def __init__(
        self,
        identity: CommonIdentityRecord,
        *,
        engine: Engine | None = None,
        env_file: str | Path | Sequence[str | Path] | None = None,
        schema: str = "core_data_model",
    ) -> None:
        self.identity = identity
        self.schema = schema
        self.source_identities: list[CommonIdentityRecord] = []
        self.identity_bundle_summary: dict[str, Any] = {}
        if engine is not None:
            self.engine = engine
        else:
            env_paths = self._normalize_env_paths(env_file)
            if env_paths:
                _load_env_files(env_paths)
            self.engine = create_engine(_build_db_url(), pool_pre_ping=True)

    @classmethod
    def from_id_me(
        cls,
        record: Mapping[str, Any],
        *,
        engine: Engine | None = None,
        env_file: str | Path | Sequence[str | Path] | None = None,
        schema: str = "core_data_model",
    ) -> "PractitionerIdentityLookup":
        return cls(
            cls._normalize_record("id.me", record),
            engine=engine,
            env_file=env_file,
            schema=schema,
        )

    @classmethod
    def from_clear_me(
        cls,
        record: Mapping[str, Any],
        *,
        engine: Engine | None = None,
        env_file: str | Path | Sequence[str | Path] | None = None,
        schema: str = "core_data_model",
    ) -> "PractitionerIdentityLookup":
        return cls(
            cls._normalize_record("clear.me", record),
            engine=engine,
            env_file=env_file,
            schema=schema,
        )

    @classmethod
    def from_login_gov(
        cls,
        record: Mapping[str, Any],
        *,
        engine: Engine | None = None,
        env_file: str | Path | Sequence[str | Path] | None = None,
        schema: str = "core_data_model",
    ) -> "PractitionerIdentityLookup":
        return cls(
            cls._normalize_record("login.gov", record),
            engine=engine,
            env_file=env_file,
            schema=schema,
        )

    @classmethod
    def from_record(
        cls,
        provider: ProviderName,
        record: Mapping[str, Any],
        *,
        engine: Engine | None = None,
        env_file: str | Path | Sequence[str | Path] | None = None,
        schema: str = "core_data_model",
    ) -> "PractitionerIdentityLookup":
        return cls(
            cls._normalize_record(provider, record),
            engine=engine,
            env_file=env_file,
            schema=schema,
        )

    @classmethod
    def from_records(
        cls,
        records: Mapping[ProviderName, Mapping[str, Any]],
        *,
        engine: Engine | None = None,
        env_file: str | Path | Sequence[str | Path] | None = None,
        schema: str = "core_data_model",
    ) -> "PractitionerIdentityLookup":
        normalized_records = {
            provider: cls._normalize_record(provider, record)
            for provider, record in records.items()
            if record is not None
        }
        if not normalized_records:
            raise ValueError("At least one provider record is required.")

        bundle_summary = cls._validate_identity_bundle(normalized_records)
        merged_identity = cls._merge_normalized_records(normalized_records)
        lookup = cls(
            merged_identity,
            engine=engine,
            env_file=env_file,
            schema=schema,
        )
        lookup.source_identities = list(normalized_records.values())
        lookup.identity_bundle_summary = bundle_summary
        return lookup

    @staticmethod
    def _normalize_env_paths(
        env_file: str | Path | Sequence[str | Path] | None,
    ) -> list[Path]:
        if env_file is None:
            return []
        if isinstance(env_file, (str, Path)):
            return [Path(env_file)]
        return [Path(item) for item in env_file]

    @classmethod
    def _normalize_record(
        cls,
        provider: ProviderName,
        record: Mapping[str, Any],
    ) -> CommonIdentityRecord:
        alias_map = cls._ALIASES.get(provider)
        if alias_map is None:
            raise ValueError(
                f"Unsupported provider {provider!r}. "
                f"Expected one of: {', '.join(sorted(cls._ALIASES))}"
            )

        raw = dict(record)
        normalized = CommonIdentityRecord(
            source=provider,
            raw_record=raw,
            subject_id=_string_or_none(_first_present(raw, alias_map["subject_id"])),
            npi=_normalize_npi(_first_present(raw, alias_map["npi"])),
            first_name=_normalize_name(_string_or_none(_first_present(raw, alias_map["first_name"]))),
            middle_name=_normalize_name(_string_or_none(_first_present(raw, alias_map["middle_name"]))),
            last_name=_normalize_name(_string_or_none(_first_present(raw, alias_map["last_name"]))),
            name_suffix=_normalize_name(_string_or_none(_first_present(raw, alias_map["name_suffix"]))),
            full_name=_normalize_name(_string_or_none(_first_present(raw, alias_map["full_name"]))),
            ssn=_digits_only(_string_or_none(_first_present(raw, alias_map["ssn"]))),
            ssn_last4=_digits_only(_string_or_none(_first_present(raw, alias_map["ssn_last4"]))),
            email=_string_or_none(_first_present(raw, alias_map["email"])),
            email_verified=_bool_or_none(_first_present(raw, alias_map["email_verified"])),
            phone=_string_or_none(_first_present(raw, alias_map["phone"])),
            phone_verified=_bool_or_none(_first_present(raw, alias_map["phone_verified"])),
            date_of_birth=_parse_date(_first_present(raw, alias_map["date_of_birth"])),
            state_license_number=_string_or_none(_first_present(raw, alias_map["state_license_number"])),
            state_license_state=_string_or_none(_first_present(raw, alias_map["state_license_state"])),
            address_line_1=_string_or_none(_first_present(raw, alias_map["address_line_1"])),
            address_line_2=_string_or_none(_first_present(raw, alias_map["address_line_2"])),
            address_city=_string_or_none(_first_present(raw, alias_map["address_city"])),
            address_state=_string_or_none(_first_present(raw, alias_map["address_state"])),
            address_postal_code=_string_or_none(_first_present(raw, alias_map["address_postal_code"])),
            address_country=_string_or_none(_first_present(raw, alias_map["address_country"])),
        )
        return normalized

    @staticmethod
    def _compare_field(
        left_value: Any,
        right_value: Any,
        *,
        label: str,
        transform: Any = None,
    ) -> tuple[bool, bool]:
        if left_value is None or right_value is None:
            return False, False
        if transform is not None:
            left_value = transform(left_value)
            right_value = transform(right_value)
        return True, left_value == right_value

    @classmethod
    def _compare_identity_pair(
        cls,
        left: CommonIdentityRecord,
        right: CommonIdentityRecord,
    ) -> dict[str, Any]:
        evidence: list[str] = []
        conflicts: list[str] = []
        link_score = 0

        compared, matched = cls._compare_field(left.npi, right.npi, label="npi")
        if compared and matched:
            evidence.append("npi_exact")
            link_score += 100
        elif compared:
            conflicts.append("npi_conflict")

        compared, matched = cls._compare_field(left.ssn_digits, right.ssn_digits, label="ssn_digits")
        if compared and matched:
            evidence.append("ssn_exact")
            link_score += 95
        elif compared:
            conflicts.append("ssn_conflict")

        compared, matched = cls._compare_field(
            left.ssn_last4_digits,
            right.ssn_last4_digits,
            label="ssn_last4_digits",
        )
        if compared and matched:
            evidence.append("ssn_last4_exact")
            link_score += 10

        compared_dob, matched_dob = cls._compare_field(
            left.date_of_birth,
            right.date_of_birth,
            label="date_of_birth",
        )
        if compared_dob and matched_dob:
            evidence.append("dob_exact")
            link_score += 15
        elif compared_dob:
            conflicts.append("date_of_birth_conflict")

        compared_first, matched_first = cls._compare_field(
            left.first_name_normalized,
            right.first_name_normalized,
            label="first_name",
            transform=lambda value: value.lower(),
        )
        compared_last, matched_last = cls._compare_field(
            left.last_name_normalized,
            right.last_name_normalized,
            label="last_name",
            transform=lambda value: value.lower(),
        )
        if compared_first and compared_last and matched_first and matched_last:
            evidence.append("name_exact")
            link_score += 35
        else:
            if compared_first and not matched_first:
                conflicts.append("first_name_conflict")
            if compared_last and not matched_last:
                conflicts.append("last_name_conflict")

        compared_phone, matched_phone = cls._compare_field(
            left.phone_digits,
            right.phone_digits,
            label="phone_digits",
        )
        if compared_phone and matched_phone:
            evidence.append("phone_exact")
            link_score += 12

        compared_email, matched_email = cls._compare_field(
            _string_or_none(left.email.lower() if left.email else None),
            _string_or_none(right.email.lower() if right.email else None),
            label="email",
        )
        if compared_email and matched_email:
            evidence.append("email_exact")
            link_score += 10

        compared_license, matched_license = cls._compare_field(
            _string_or_none(left.state_license_number.lower() if left.state_license_number else None),
            _string_or_none(right.state_license_number.lower() if right.state_license_number else None),
            label="state_license_number",
        )
        if compared_license and matched_license:
            compared_state, matched_state = cls._compare_field(
                _string_or_none(left.state_license_state.upper() if left.state_license_state else None),
                _string_or_none(right.state_license_state.upper() if right.state_license_state else None),
                label="state_license_state",
            )
            if not compared_state or matched_state:
                evidence.append("state_license_exact")
                link_score += 20

        if "name_exact" in evidence and "dob_exact" in evidence:
            evidence.append("name_and_dob_exact")
            link_score += 25

        if "name_exact" in evidence and "phone_exact" in evidence:
            evidence.append("name_and_phone_exact")
            link_score += 15

        return {
            "left_source": left.source,
            "right_source": right.source,
            "evidence": evidence,
            "conflicts": conflicts,
            "link_score": link_score,
            "is_compatible": not conflicts,
            "has_linking_evidence": bool(evidence),
        }

    @classmethod
    def _validate_identity_bundle(
        cls,
        records: Mapping[ProviderName, CommonIdentityRecord],
    ) -> dict[str, Any]:
        identities = list(records.values())
        if len(identities) == 1:
            return {
                "bundle_validated": True,
                "pairwise_checks": [],
                "connected_sources": [identities[0].source],
                "providers": [identities[0].source],
            }

        pairwise_checks: list[dict[str, Any]] = []
        adjacency: dict[str, set[str]] = {identity.source: set() for identity in identities}
        blocking_conflicts: list[dict[str, Any]] = []

        for index, left in enumerate(identities):
            for right in identities[index + 1 :]:
                pair_summary = cls._compare_identity_pair(left, right)
                pairwise_checks.append(pair_summary)
                if pair_summary["conflicts"]:
                    blocking_conflicts.append(pair_summary)
                if pair_summary["has_linking_evidence"] and pair_summary["is_compatible"]:
                    adjacency[left.source].add(right.source)
                    adjacency[right.source].add(left.source)

        if blocking_conflicts:
            raise PractitionerMatchError(
                "Provider records conflict and do not appear to describe the same person:\n"
                + json.dumps(blocking_conflicts, indent=2, default=str)
            )

        visited: set[str] = set()
        stack = [identities[0].source]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            stack.extend(sorted(adjacency[current] - visited))

        if len(visited) != len(identities):
            disconnected = sorted(set(adjacency) - visited)
            raise PractitionerMatchError(
                "Provider records could not be linked strongly enough to confirm they describe the same person:\n"
                + json.dumps(
                    {
                        "pairwise_checks": pairwise_checks,
                        "disconnected_sources": disconnected,
                    },
                    indent=2,
                    default=str,
                )
            )

        return {
            "bundle_validated": True,
            "pairwise_checks": pairwise_checks,
            "connected_sources": sorted(visited),
            "providers": sorted(records),
        }

    @classmethod
    def _ordered_records(
        cls,
        records: Mapping[ProviderName, CommonIdentityRecord],
    ) -> list[CommonIdentityRecord]:
        priority = {provider: index for index, provider in enumerate(MERGE_PROVIDER_PRIORITY)}
        return sorted(
            records.values(),
            key=lambda record: (priority.get(record.source, len(priority)), record.source),
        )

    @staticmethod
    def _pick_first_non_empty(values: Iterable[Any]) -> Any:
        for value in values:
            if value is None:
                continue
            if isinstance(value, str) and not value.strip():
                continue
            return value
        return None

    @classmethod
    def _pick_best_email(cls, records: Sequence[CommonIdentityRecord]) -> str | None:
        verified = [record.email for record in records if record.email and record.email_verified]
        return cls._pick_first_non_empty(verified or [record.email for record in records])

    @classmethod
    def _pick_best_phone(cls, records: Sequence[CommonIdentityRecord]) -> str | None:
        verified = [record.phone for record in records if record.phone and record.phone_verified]
        return cls._pick_first_non_empty(verified or [record.phone for record in records])

    @classmethod
    def _merge_normalized_records(
        cls,
        records: Mapping[ProviderName, CommonIdentityRecord],
    ) -> CommonIdentityRecord:
        ordered_records = cls._ordered_records(records)
        merged_source = "merged:" + "+".join(record.source for record in ordered_records)
        raw_record = {record.source: record.raw_record for record in ordered_records}
        first_name = cls._pick_first_non_empty(record.first_name for record in ordered_records)
        middle_name = cls._pick_first_non_empty(record.middle_name for record in ordered_records)
        last_name = cls._pick_first_non_empty(record.last_name for record in ordered_records)
        full_name = cls._pick_first_non_empty(record.full_name for record in ordered_records)
        if full_name is None:
            full_name = _pick_joined_name(first_name, middle_name, last_name)

        return CommonIdentityRecord(
            source=merged_source,
            raw_record=raw_record,
            subject_id=cls._pick_first_non_empty(record.subject_id for record in ordered_records),
            npi=cls._pick_first_non_empty(record.npi for record in ordered_records),
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            name_suffix=cls._pick_first_non_empty(record.name_suffix for record in ordered_records),
            full_name=full_name,
            ssn=cls._pick_first_non_empty(record.ssn for record in ordered_records),
            ssn_last4=cls._pick_first_non_empty(record.ssn_last4 for record in ordered_records),
            email=cls._pick_best_email(ordered_records),
            email_verified=cls._pick_first_non_empty(
                record.email_verified for record in ordered_records if record.email_verified is not None
            ),
            phone=cls._pick_best_phone(ordered_records),
            phone_verified=cls._pick_first_non_empty(
                record.phone_verified for record in ordered_records if record.phone_verified is not None
            ),
            date_of_birth=cls._pick_first_non_empty(record.date_of_birth for record in ordered_records),
            state_license_number=cls._pick_first_non_empty(
                record.state_license_number for record in ordered_records
            ),
            state_license_state=cls._pick_first_non_empty(
                record.state_license_state for record in ordered_records
            ),
            address_line_1=cls._pick_first_non_empty(record.address_line_1 for record in ordered_records),
            address_line_2=cls._pick_first_non_empty(record.address_line_2 for record in ordered_records),
            address_city=cls._pick_first_non_empty(record.address_city for record in ordered_records),
            address_state=cls._pick_first_non_empty(record.address_state for record in ordered_records),
            address_postal_code=cls._pick_first_non_empty(
                record.address_postal_code for record in ordered_records
            ),
            address_country=cls._pick_first_non_empty(record.address_country for record in ordered_records),
        )

    def resolve(self) -> PractitionerResolution:
        candidate = self.find_best_practitioner_match()
        profile = self.fetch_practitioner_profile(candidate.practitioner_id)
        return PractitionerResolution(
            identity=self.identity,
            matched_candidate=candidate,
            profile=profile,
            source_identities=list(getattr(self, "source_identities", [])),
            identity_bundle_summary=dict(getattr(self, "identity_bundle_summary", {})),
        )

    def find_best_practitioner_match(self) -> PractitionerMatchCandidate:
        sql = text(
            f"""
            WITH practitioner_name AS (
                SELECT
                    pn.practitioner_id,
                    pn.first_name,
                    pn.middle_name,
                    pn.last_name,
                    pn.is_primary,
                    ROW_NUMBER() OVER (
                        PARTITION BY pn.practitioner_id
                        ORDER BY pn.is_primary DESC NULLS LAST, pn.inserted_datetime DESC NULLS LAST, pn.person_name_id
                    ) AS rn
                FROM {self.schema}.person_names pn
                WHERE pn.practitioner_id IS NOT NULL
            ),
            practitioner_phone AS (
                SELECT
                    pp.practitioner_id,
                    regexp_replace(COALESCE(ph.country_code, '') || COALESCE(ph.area_code, '') || COALESCE(ph.phone_number, ''), '\\D', '', 'g') AS phone_digits
                FROM {self.schema}.practitioner_phone pp
                JOIN {self.schema}.phone_number ph
                  ON ph.phone_number_id = pp.phone_number_id
            ),
            practitioner_license AS (
                SELECT
                    sl.practitioner_id,
                    sl.state_code,
                    sl.license_number
                FROM {self.schema}.state_license sl
            ),
            candidates AS (
                SELECT
                    p.practitioner_id,
                    p.npi_id,
                    p.date_of_birth,
                    pn.first_name,
                    pn.middle_name,
                    pn.last_name,
                    lic.state_code,
                    lic.license_number,
                    (
                        CASE WHEN :match_npi IS NOT NULL AND p.npi_id = :match_npi THEN {MATCH_WEIGHT_NPI_EXACT} ELSE 0 END
                        + CASE
                            WHEN :ssn_digits IS NOT NULL
                             AND regexp_replace(COALESCE(p.social_security_number, ''), '\D', '', 'g') = :ssn_digits
                            THEN {MATCH_WEIGHT_SSN_EXACT} ELSE 0
                          END
                        + CASE
                            WHEN :ssn_last4 IS NOT NULL
                             AND right(regexp_replace(COALESCE(p.social_security_number, ''), '\D', '', 'g'), 4) = :ssn_last4
                            THEN {MATCH_WEIGHT_SSN_LAST4} ELSE 0
                          END
                        + CASE
                            WHEN :first_name IS NOT NULL AND :last_name IS NOT NULL
                             AND lower(COALESCE(pn.first_name, '')) = lower(:first_name)
                             AND lower(COALESCE(pn.last_name, '')) = lower(:last_name)
                            THEN {MATCH_WEIGHT_NAME_EXACT} ELSE 0
                          END
                        + CASE
                            WHEN :middle_name IS NOT NULL
                             AND lower(COALESCE(pn.middle_name, '')) = lower(:middle_name)
                            THEN {MATCH_WEIGHT_MIDDLE_NAME_EXACT} ELSE 0
                          END
                        + CASE
                            WHEN :dob IS NOT NULL AND p.date_of_birth = :dob
                            THEN {MATCH_WEIGHT_DOB_EXACT} ELSE 0
                          END
                        + CASE
                            WHEN :phone_digits IS NOT NULL AND EXISTS (
                                SELECT 1
                                FROM practitioner_phone phone_match
                                WHERE phone_match.practitioner_id = p.practitioner_id
                                  AND right(phone_match.phone_digits, 10) = right(:phone_digits, 10)
                            )
                            THEN {MATCH_WEIGHT_PHONE_EXACT} ELSE 0
                          END
                        + CASE
                            WHEN :license_number IS NOT NULL AND EXISTS (
                                SELECT 1
                                FROM practitioner_license lic_match
                                WHERE lic_match.practitioner_id = p.practitioner_id
                                  AND lower(COALESCE(lic_match.license_number, '')) = lower(:license_number)
                                  AND (
                                      :license_state IS NULL
                                      OR upper(COALESCE(lic_match.state_code, '')) = upper(:license_state)
                                  )
                            )
                            THEN {MATCH_WEIGHT_STATE_LICENSE_EXACT} ELSE 0
                          END
                    ) AS score,
                    ARRAY_REMOVE(ARRAY[
                        CASE WHEN :match_npi IS NOT NULL AND p.npi_id = :match_npi THEN 'npi_exact' END,
                        CASE
                            WHEN :ssn_digits IS NOT NULL
                             AND regexp_replace(COALESCE(p.social_security_number, ''), '\D', '', 'g') = :ssn_digits
                            THEN 'ssn_exact'
                        END,
                        CASE
                            WHEN :ssn_last4 IS NOT NULL
                             AND right(regexp_replace(COALESCE(p.social_security_number, ''), '\D', '', 'g'), 4) = :ssn_last4
                            THEN 'ssn_last4'
                        END,
                        CASE
                            WHEN :first_name IS NOT NULL AND :last_name IS NOT NULL
                             AND lower(COALESCE(pn.first_name, '')) = lower(:first_name)
                             AND lower(COALESCE(pn.last_name, '')) = lower(:last_name)
                            THEN 'name_exact'
                        END,
                        CASE
                            WHEN :middle_name IS NOT NULL
                             AND lower(COALESCE(pn.middle_name, '')) = lower(:middle_name)
                            THEN 'middle_name_exact'
                        END,
                        CASE WHEN :dob IS NOT NULL AND p.date_of_birth = :dob THEN 'dob_exact' END,
                        CASE
                            WHEN :phone_digits IS NOT NULL AND EXISTS (
                                SELECT 1
                                FROM practitioner_phone phone_match
                                WHERE phone_match.practitioner_id = p.practitioner_id
                                  AND right(phone_match.phone_digits, 10) = right(:phone_digits, 10)
                            )
                            THEN 'phone_exact'
                        END,
                        CASE
                            WHEN :license_number IS NOT NULL AND EXISTS (
                                SELECT 1
                                FROM practitioner_license lic_match
                                WHERE lic_match.practitioner_id = p.practitioner_id
                                  AND lower(COALESCE(lic_match.license_number, '')) = lower(:license_number)
                                  AND (
                                      :license_state IS NULL
                                      OR upper(COALESCE(lic_match.state_code, '')) = upper(:license_state)
                                  )
                            )
                            THEN 'state_license_exact'
                        END
                    ], NULL) AS score_breakdown
                FROM {self.schema}.practitioner p
                LEFT JOIN practitioner_name pn
                  ON pn.practitioner_id = p.practitioner_id
                 AND pn.rn = 1
                LEFT JOIN practitioner_license lic
                  ON lic.practitioner_id = p.practitioner_id
                WHERE
                    (:match_npi IS NOT NULL AND p.npi_id = :match_npi)
                    OR (
                        :ssn_digits IS NOT NULL
                        AND regexp_replace(COALESCE(p.social_security_number, ''), '\D', '', 'g') = :ssn_digits
                    )
                    OR (
                        :ssn_last4 IS NOT NULL
                        AND right(regexp_replace(COALESCE(p.social_security_number, ''), '\D', '', 'g'), 4) = :ssn_last4
                    )
                    OR (
                        :first_name IS NOT NULL
                        AND :last_name IS NOT NULL
                        AND lower(COALESCE(pn.first_name, '')) = lower(:first_name)
                        AND lower(COALESCE(pn.last_name, '')) = lower(:last_name)
                    )
                    OR (
                        :license_number IS NOT NULL
                        AND lower(COALESCE(lic.license_number, '')) = lower(:license_number)
                    )
                    OR (
                        :phone_digits IS NOT NULL
                        AND EXISTS (
                            SELECT 1
                            FROM practitioner_phone phone_match
                            WHERE phone_match.practitioner_id = p.practitioner_id
                              AND right(phone_match.phone_digits, 10) = right(:phone_digits, 10)
                        )
                    )
            )
            SELECT DISTINCT
                practitioner_id,
                npi_id,
                trim(concat_ws(' ', first_name, middle_name, last_name)) AS matched_name,
                date_of_birth,
                license_number AS state_license_number,
                state_code AS state_license_state,
                score,
                score_breakdown
            FROM candidates
            WHERE score > 0
            ORDER BY score DESC, npi_id NULLS LAST, practitioner_id
            LIMIT 5
            """
        )
        params = {
            "match_npi": self.identity.npi,
            "ssn_digits": self.identity.ssn_digits,
            "ssn_last4": self.identity.ssn_last4_digits,
            "first_name": self.identity.first_name_normalized,
            "middle_name": self.identity.middle_name_normalized,
            "last_name": self.identity.last_name_normalized,
            "dob": self.identity.date_of_birth,
            "phone_digits": self.identity.phone_digits,
            "license_number": self.identity.state_license_number,
            "license_state": self.identity.state_license_state,
        }

        with self.engine.connect() as conn:
            rows = [dict(row) for row in conn.execute(sql, params).mappings().all()]

        if not rows:
            raise PractitionerMatchError(
                "No practitioner match found for normalized identity record:\n"
                + json.dumps(self._json_ready_identity(), indent=2, default=str)
            )

        top = rows[0]
        if len(rows) > 1 and rows[1]["score"] == top["score"]:
            raise PractitionerMatchError(
                "Practitioner match is ambiguous; top candidates share the same score:\n"
                + json.dumps(rows, indent=2, default=str)
            )

        return PractitionerMatchCandidate(
            practitioner_id=str(top["practitioner_id"]),
            npi_id=top["npi_id"],
            matched_name=top["matched_name"],
            date_of_birth=top["date_of_birth"],
            state_license_number=top["state_license_number"],
            state_license_state=top["state_license_state"],
            score=int(top["score"]),
            score_breakdown=list(top["score_breakdown"] or []),
        )

    def fetch_practitioner_profile(self, practitioner_id: str) -> dict[str, Any]:
        sql = text(
            f"""
            SELECT json_build_object(
                'practitioner', (
                    SELECT row_to_json(p_row)
                    FROM (
                        SELECT
                            p.practitioner_id,
                            p.npi_id,
                            p.organization_id,
                            p.legal_entity_id,
                            p.gender_code,
                            p.date_of_birth,
                            p.state_of_birth_code,
                            p.country_of_birth_code,
                            p.irs_individual_tax_identification_number,
                            p.social_security_number,
                            p.other_credential_text,
                            p.source_file_id,
                            p.inserted_datetime,
                            p.source_data_datetime
                        FROM {self.schema}.practitioner p
                        WHERE p.practitioner_id = :practitioner_id
                    ) p_row
                ),
                'names', COALESCE((
                    SELECT json_agg(row_to_json(name_row) ORDER BY name_row.is_primary DESC NULLS LAST, name_row.inserted_datetime DESC NULLS LAST)
                    FROM (
                        SELECT
                            pn.person_name_id,
                            pn.name_prefix,
                            pn.first_name,
                            pn.middle_name,
                            pn.last_name,
                            pn.name_suffix,
                            pn.full_name,
                            pn.name_type,
                            pn.is_primary,
                            pn.effective_start_date,
                            pn.effective_end_date,
                            pn.source_file_id,
                            pn.inserted_datetime,
                            pn.source_data_datetime
                        FROM {self.schema}.person_names pn
                        WHERE pn.practitioner_id = :practitioner_id
                    ) name_row
                ), '[]'::json),
                'npis', COALESCE((
                    SELECT json_agg(row_to_json(npi_row) ORDER BY npi_row.is_primary_npi DESC NULLS LAST, npi_row.npi_id)
                    FROM (
                        SELECT
                            pn.practitioner_npi_id,
                            pn.npi_id,
                            pn.is_sole_proprietor,
                            (pn.npi_id = p.npi_id) AS is_primary_npi,
                            n.entity_type_code,
                            n.credential_text,
                            n.employer_identification_number,
                            n.npi_deactivation_reason_code,
                            n.npi_deactivation_date,
                            n.npi_reactivation_date
                        FROM {self.schema}.practitioner_npi pn
                        LEFT JOIN {self.schema}.npi n
                          ON n.npi_id = pn.npi_id
                        JOIN {self.schema}.practitioner p
                          ON p.practitioner_id = pn.practitioner_id
                        WHERE pn.practitioner_id = :practitioner_id
                    ) npi_row
                ), '[]'::json),
                'state_licenses', COALESCE((
                    SELECT json_agg(row_to_json(license_row) ORDER BY license_row.state_code, license_row.license_number)
                    FROM (
                        SELECT
                            sl.state_license_id,
                            sl.npi_id,
                            sl.state_code,
                            sl.license_number
                        FROM {self.schema}.state_license sl
                        WHERE sl.practitioner_id = :practitioner_id
                    ) license_row
                ), '[]'::json),
                'phones', COALESCE((
                    SELECT json_agg(row_to_json(phone_row) ORDER BY phone_row.is_preferred DESC NULLS LAST, phone_row.phone_type, phone_row.phone_number)
                    FROM (
                        SELECT
                            pp.practitioner_phone_id,
                            pp.organization_id,
                            pp.is_preferred,
                            ph.phone_number_id,
                            ph.country_code,
                            ph.area_code,
                            ph.phone_number,
                            ph.phone_extension,
                            ph.phone_type,
                            ph.is_primary,
                            ph.source_file_id,
                            ph.inserted_datetime,
                            ph.source_data_datetime
                        FROM {self.schema}.practitioner_phone pp
                        JOIN {self.schema}.phone_number ph
                          ON ph.phone_number_id = pp.phone_number_id
                        WHERE pp.practitioner_id = :practitioner_id
                    ) phone_row
                ), '[]'::json),
                'locations', COALESCE((
                    SELECT json_agg(row_to_json(location_row) ORDER BY location_row.location_id)
                    FROM (
                        SELECT
                            l.location_id,
                            l.organization_id,
                            l.npi_id,
                            l.address_use,
                            l.smarty_key,
                            l.source_file_id,
                            l.inserted_datetime,
                            l.source_data_datetime,
                            json_build_object(
                                'location_us_id', lu.location_us_id,
                                'delivery_line_1', lu.delivery_line_1,
                                'delivery_line_2', lu.delivery_line_2,
                                'city_name', lu.city_name,
                                'state_abbreviation', lu.state_abbreviation,
                                'zipcode', lu.zipcode,
                                'plus4_code', lu.plus4_code,
                                'county_name', lu.county_name,
                                'latitude', lu.latitude,
                                'longitude', lu.longitude
                            ) AS us_address,
                            json_build_object(
                                'location_international_id', li.location_international_id,
                                'location', li.location,
                                'locality', li.locality,
                                'administrative_area', li.administrative_area,
                                'postal_code', li.postal_code,
                                'country', li.country
                            ) AS international_address,
                            json_build_object(
                                'location_nonstandard_id', ln.location_nonstandard_id,
                                'location_line', ln.location_line,
                                'city', ln.city,
                                'administrative_area', ln.administrative_area,
                                'postal_code', ln.postal_code,
                                'province', ln.province,
                                'foreign_country_name', ln.foreign_country_name
                            ) AS nonstandard_address
                        FROM {self.schema}.location l
                        LEFT JOIN {self.schema}.location_us lu
                          ON lu.location_us_id = l.location_us_id
                        LEFT JOIN {self.schema}.location_international li
                          ON li.location_international_id = l.location_international_id
                        LEFT JOIN {self.schema}.location_nonstandard ln
                          ON ln.location_nonstandard_id = l.location_nonstandard_id
                        WHERE l.practitioner_id = :practitioner_id
                    ) location_row
                ), '[]'::json),
                'phone_locations', COALESCE((
                    SELECT json_agg(row_to_json(pl_row) ORDER BY pl_row.practitioner_phone_location_id)
                    FROM (
                        SELECT
                            ppl.practitioner_phone_location_id,
                            ppl.location_id,
                            ppl.phone_number_id,
                            link.practitioner_location_phone_linktype
                        FROM {self.schema}.practitioner_phone_location ppl
                        LEFT JOIN {self.schema}.practitioner_location_phone_linktype link
                          ON link.practitioner_location_phone_linktype_id = ppl.practitioner_location_phone_linktype_id
                        WHERE ppl.practitioner_id = :practitioner_id
                    ) pl_row
                ), '[]'::json),
                'organizations', COALESCE((
                    SELECT json_agg(row_to_json(org_row) ORDER BY org_row.organization_name, org_row.organization_id)
                    FROM (
                        SELECT
                            pto.practitioner_to_organization,
                            o.organization_id,
                            o.npi_id,
                            o.organization_name,
                            o.is_active,
                            o.is_fhir_server,
                            o.is_data_network,
                            o.is_payer,
                            o.location_id
                        FROM {self.schema}.practitioner_to_organization pto
                        JOIN {self.schema}.organization o
                          ON o.organization_id = pto.organization_id
                        WHERE pto.practitioner_id = :practitioner_id
                    ) org_row
                ), '[]'::json),
                'authorized_individual_links', COALESCE((
                    SELECT json_agg(row_to_json(ai_row) ORDER BY ai_row.is_official DESC NULLS LAST, ai_row.authorized_individual_id)
                    FROM (
                        SELECT
                            ai.authorized_individual_id,
                            ai.organization_id,
                            ai.is_official,
                            ai.title_or_position,
                            ai.authorization_start_date,
                            ai.authorization_end_date,
                            ai.phone_number_id,
                            ai.location_id,
                            ai.source_file_id,
                            ai.inserted_datetime,
                            ai.source_data_datetime
                        FROM {self.schema}.authorized_individual ai
                        WHERE ai.practitioner_id = :practitioner_id
                    ) ai_row
                ), '[]'::json),
                'roles', COALESCE((
                    SELECT json_agg(row_to_json(role_row) ORDER BY role_row.is_current DESC NULLS LAST, role_row.display_name, role_row.code)
                    FROM (
                        SELECT
                            pr.practitioner_role_id,
                            pr.role_type,
                            pr.has_nppes,
                            pr.has_pecos,
                            pr.authoritative_source,
                            pr.start_date,
                            pr.end_date,
                            pr.is_current,
                            tc.taxonomy_code_id,
                            tc.code,
                            tc.display_name,
                            tc.definition
                        FROM {self.schema}.practitioner_role pr
                        LEFT JOIN {self.schema}.taxonomy_code tc
                          ON tc.taxonomy_code_id = pr.taxonomy_code_id
                        WHERE pr.practitioner_id = :practitioner_id
                    ) role_row
                ), '[]'::json),
                'professional_credentials', COALESCE((
                    SELECT json_agg(row_to_json(cred_row) ORDER BY cred_row.credential_type, cred_row.prof_cred_code)
                    FROM (
                        SELECT
                            pc.prof_cred_id,
                            pc.organization_id,
                            pc.npi_id,
                            pc.credential_type,
                            pc.prof_cred_code,
                            pc.prof_cred_status,
                            pc.is_primary,
                            pc.prof_cred_effective_date,
                            pc.issue_date,
                            pc.expiration_date,
                            tc.code AS taxonomy_code,
                            tc.display_name AS taxonomy_display_name
                        FROM {self.schema}.prof_cred pc
                        LEFT JOIN {self.schema}.taxonomy_code tc
                          ON tc.taxonomy_code_id = pc.taxonomy_code_id
                        WHERE pc.practitioner_id = :practitioner_id
                    ) cred_row
                ), '[]'::json),
                'authority_assertions', COALESCE((
                    SELECT json_agg(row_to_json(auth_row) ORDER BY auth_row.source_updated_ts DESC NULLS LAST, auth_row.provider_authority_assertion_id)
                    FROM (
                        SELECT
                            paa.provider_authority_assertion_id,
                            paa.authorized_individual_id,
                            paa.represented_organization_id,
                            paa.provider_npi,
                            paa.organization_npi,
                            paa.source_system,
                            paa.authority_record_type,
                            paa.provider_type,
                            paa.authority_role_cd,
                            paa.authority_role_desc,
                            paa.authority_display_name,
                            paa.authority_first_name,
                            paa.authority_middle_name,
                            paa.authority_last_name,
                            paa.authority_suffix_cd,
                            paa.authority_credential_text,
                            paa.authority_title_text,
                            paa.authority_phone_raw,
                            paa.authority_email,
                            paa.authority_line_1,
                            paa.authority_line_2,
                            paa.authority_city,
                            paa.authority_state,
                            paa.authority_postal_code,
                            paa.certification_signature_date,
                            paa.authority_effective_date,
                            paa.authority_end_date,
                            paa.authority_status_cd,
                            paa.source_created_ts,
                            paa.source_updated_ts
                        FROM {self.schema}.provider_authority_assertion paa
                        WHERE paa.represented_practitioner_id = :practitioner_id
                    ) auth_row
                ), '[]'::json)
            ) AS profile
            """
        )

        with self.engine.connect() as conn:
            row = conn.execute(sql, {"practitioner_id": practitioner_id}).mappings().one_or_none()

        if row is None or row["profile"] is None:
            raise PractitionerMatchError(
                f"Practitioner {practitioner_id} was matched but no profile could be loaded."
            )

        profile = dict(row["profile"])
        profile["resolved_identity"] = self._json_ready_identity()
        return profile

    def _json_ready_identity(self) -> dict[str, Any]:
        return asdict(self.identity)


def _load_json_input(
    *,
    json_file: str | None,
    json_text: str | None,
) -> dict[str, Any]:
    if json_file and json_text:
        raise ValueError("Pass either --json-file or --json-text, not both.")
    if json_file:
        return json.loads(Path(json_file).read_text(encoding="utf-8"))
    if json_text:
        return json.loads(json_text)

    import sys

    if sys.stdin.isatty():
        raise ValueError("Provide input with --json-file, --json-text, or stdin.")
    stdin_text = sys.stdin.read()
    if not stdin_text.strip():
        raise ValueError("Stdin was empty.")
    return json.loads(stdin_text)


def _load_json_file(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Normalize an identity-provider record, resolve a CoreDM practitioner, "
            "and print the matched profile as JSON."
        )
    )
    parser.add_argument(
        "--provider",
        default=None,
        choices=["id.me", "clear.me", "login.gov"],
        help="Identity provider record format to normalize in single-record mode.",
    )
    parser.add_argument(
        "--json-file",
        default=None,
        help="Path to a JSON file containing the provider record.",
    )
    parser.add_argument(
        "--json-text",
        default=None,
        help="Inline JSON payload containing the provider record.",
    )
    parser.add_argument(
        "--env-file",
        action="append",
        default=[],
        help="Optional dotenv file(s) used to load DB connection settings.",
    )
    parser.add_argument(
        "--schema",
        default="core_data_model",
        help="Target CoreDM schema name. Defaults to core_data_model.",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level for output. Defaults to 2.",
    )
    parser.add_argument(
        "--id-me-file",
        default=None,
        help="JSON file for an id.me record in bundle mode.",
    )
    parser.add_argument(
        "--clear-me-file",
        default=None,
        help="JSON file for a clear.me record in bundle mode.",
    )
    parser.add_argument(
        "--login-gov-file",
        default=None,
        help="JSON file for a login.gov record in bundle mode.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_cli_parser()
    args = parser.parse_args(argv)

    try:
        print("ARGUMENTS=",args)
        bundle_records = {
            provider: _load_json_file(path)
            for provider, path in (
                ("id.me", args.id_me_file),
                ("clear.me", args.clear_me_file),
                ("login.gov", args.login_gov_file),
            )
            if path
        }

        if bundle_records:
            if args.provider or args.json_file or args.json_text:
                raise ValueError(
                    "Bundle mode cannot be combined with --provider, --json-file, or --json-text."
                )
            lookup = PractitionerIdentityLookup.from_records(
                bundle_records,
                env_file=args.env_file,
                schema=args.schema,
            )
        else:
            if args.provider is None:
                raise ValueError(
                    "Pass --provider for single-record mode, or use --id-me-file / "
                    "--clear-me-file / --login-gov-file for bundle mode."
                )
            record = _load_json_input(json_file=args.json_file, json_text=args.json_text)
            lookup = PractitionerIdentityLookup.from_record(
                args.provider,
                record,
                env_file=args.env_file,
                schema=args.schema,
            )
        resolution = lookup.resolve()
    except Exception as exc:
        parser.exit(
            1,
            f"ERROR: {exc}\n",
        )

    payload = {
        "identity": asdict(resolution.identity),
        "source_identities": [asdict(identity) for identity in resolution.source_identities],
        "identity_bundle_summary": resolution.identity_bundle_summary,
        "matched_candidate": asdict(resolution.matched_candidate),
        "profile": resolution.profile,
    }
    print(json.dumps(payload, indent=args.indent, default=str))
    return 0


__all__ = [
    "CommonIdentityRecord",
    "PractitionerIdentityLookup",
    "PractitionerMatchCandidate",
    "PractitionerMatchError",
    "PractitionerResolution",
]


if __name__ == "__main__":
    raise SystemExit(main())
