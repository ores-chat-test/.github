#!/usr/bin/env python3
"""Validate an ORES Chat test-suite declaration without third-party packages."""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


SUITE_PATTERN = re.compile(r"^[a-z0-9][a-z0-9.-]{2,99}$")
ASSERTION_PATTERN = re.compile(r"^[a-z][a-z0-9-]{2,79}$")
OWNER_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,38}$")
SURFACES = {"public", "customer", "admin", "internal", "packaging", "recovery"}
ENVIRONMENTS = {"main-org", "test-org"}
EVIDENCE = {"contract", "local", "hosted", "live"}
FORBIDDEN_TEXT = re.compile(
    r"(?:bearer\s+[a-z0-9._~+/=-]+|database_url\s*=|api[_-]?key\s*=|\.tsx?\b|jsx\b|react\b)",
    re.IGNORECASE,
)


class ValidationError(ValueError):
    """A declaration violated the executable test-fleet contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def _string_list(value: Any, field: str) -> list[str]:
    _require(isinstance(value, list), f"{field} must be an array")
    _require(all(isinstance(item, str) for item in value), f"{field} must contain strings")
    _require(len(value) == len(set(value)), f"{field} must not contain duplicates")
    return value


def validate(document: Any, repository: str | None = None) -> None:
    _require(isinstance(document, dict), "root must be an object")
    expected_keys = {"version", "suite", "status", "surfaces", "environments", "assertions", "owners"}
    _require(set(document) == expected_keys, "root fields must match the version 1 schema exactly")
    _require(document["version"] == 1, "version must be 1")

    suite = document["suite"]
    _require(isinstance(suite, str) and SUITE_PATTERN.fullmatch(suite) is not None, "suite is invalid")
    if repository:
        expected_suite = repository.rsplit("/", 1)[-1]
        _require(suite == expected_suite, f"suite must match repository name {expected_suite!r}")

    status = document["status"]
    _require(status in {"contract-only", "live"}, "status must be contract-only or live")

    surfaces = _string_list(document["surfaces"], "surfaces")
    _require(bool(surfaces) and set(surfaces) <= SURFACES, "surfaces contains an unsupported trust plane")

    environments = _string_list(document["environments"], "environments")
    _require(set(environments) == ENVIRONMENTS, "environments must contain main-org and test-org exactly")

    assertions = document["assertions"]
    _require(isinstance(assertions, list) and len(assertions) >= 3, "assertions must contain at least three entries")
    assertion_ids: set[str] = set()
    evidence_seen: set[str] = set()
    for index, assertion in enumerate(assertions):
        prefix = f"assertions[{index}]"
        _require(isinstance(assertion, dict), f"{prefix} must be an object")
        _require(set(assertion) == {"id", "description", "evidence"}, f"{prefix} fields are invalid")
        assertion_id = assertion["id"]
        description = assertion["description"]
        evidence = assertion["evidence"]
        _require(
            isinstance(assertion_id, str) and ASSERTION_PATTERN.fullmatch(assertion_id) is not None,
            f"{prefix}.id is invalid",
        )
        _require(assertion_id not in assertion_ids, f"duplicate assertion id {assertion_id!r}")
        assertion_ids.add(assertion_id)
        _require(isinstance(description, str) and 12 <= len(description) <= 300, f"{prefix}.description is invalid")
        _require(FORBIDDEN_TEXT.search(description) is None, f"{prefix}.description contains forbidden technology or secret material")
        _require(evidence in EVIDENCE, f"{prefix}.evidence is invalid")
        evidence_seen.add(evidence)

    if status == "live":
        _require("live" in evidence_seen, "a live suite must declare at least one live assertion")
    else:
        _require("live" not in evidence_seen, "a contract-only suite cannot claim live evidence")

    owners = _string_list(document["owners"], "owners")
    _require(bool(owners), "owners must not be empty")
    _require(all(OWNER_PATTERN.fullmatch(owner) is not None for owner in owners), "owners contains an invalid GitHub login")


def validate_path(path: Path) -> None:
    document = json.loads(path.read_text(encoding="utf-8"))
    validate(document, os.environ.get("GITHUB_REPOSITORY"))


def self_test() -> None:
    valid = {
        "version": 1,
        "suite": "example-e2e",
        "status": "contract-only",
        "surfaces": ["public", "customer"],
        "environments": ["main-org", "test-org"],
        "assertions": [
            {"id": "public-route", "description": "Public requests use the public route.", "evidence": "contract"},
            {"id": "customer-auth", "description": "Customer requests require customer authority.", "evidence": "local"},
            {"id": "admin-rejected", "description": "Administrator credentials are rejected here.", "evidence": "hosted"},
        ],
        "owners": ["ores-chat"],
    }
    validate(valid)
    invalid = json.loads(json.dumps(valid))
    invalid["status"] = "live"
    try:
        validate(invalid)
    except ValidationError:
        pass
    else:
        raise AssertionError("self-test expected live evidence validation to fail")

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "suite.json"
        path.write_text(json.dumps(valid), encoding="utf-8")
        validate(json.loads(path.read_text(encoding="utf-8")))


def main() -> int:
    try:
        if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
            self_test()
            print("test-suite validator self-test passed")
            return 0
        path = Path(sys.argv[1] if len(sys.argv) > 1 else "suite.json")
        validate_path(path)
        print(f"validated {path}")
        return 0
    except (OSError, json.JSONDecodeError, ValidationError, AssertionError) as error:
        print(f"validation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
