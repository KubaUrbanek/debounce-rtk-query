#!/usr/bin/env python3
"""Collect a compact, sanitized OpenCode session corpus for local analysis."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


def run_json(command: list[str]) -> Any:
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown error"
        raise RuntimeError(f"{' '.join(command)} failed: {detail}")
    raw = result.stdout.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{' '.join(command)} did not return JSON: {exc}") from exc


def first(mapping: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = mapping.get(key)
        if value is not None:
            return value
    return None


def nested(mapping: dict[str, Any], *keys: str) -> Any:
    current: Any = mapping
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def session_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("sessions", "items", "data", "result"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    raise RuntimeError("Unsupported `opencode session list --format json` shape")


def session_id(row: dict[str, Any]) -> str | None:
    value = first(row, "id", "sessionID", "sessionId", "session_id")
    return str(value) if value else None


def parse_time(value: Any) -> dt.datetime | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        timestamp = float(value)
        if timestamp > 10_000_000_000:
            timestamp /= 1000
        return dt.datetime.fromtimestamp(timestamp, tz=dt.timezone.utc)
    if isinstance(value, str):
        text = value.replace("Z", "+00:00")
        try:
            parsed = dt.datetime.fromisoformat(text)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=dt.timezone.utc)
        except ValueError:
            return None
    return None


def row_time(row: dict[str, Any]) -> Any:
    return first(row, "updated", "updatedAt", "updated_at", "created", "createdAt") or nested(row, "time", "updated") or nested(row, "time", "created")


def row_project(row: dict[str, Any]) -> str | None:
    value = first(row, "directory", "path", "project", "worktree") or nested(row, "project", "worktree")
    return str(value) if value else None


def path_matches(candidate: str | None, requested: str | None) -> bool:
    if not requested:
        return True
    if not candidate:
        return False
    try:
        return Path(candidate).expanduser().resolve() == Path(requested).expanduser().resolve()
    except OSError:
        return os.path.normcase(os.path.abspath(candidate)) == os.path.normcase(os.path.abspath(requested))


def find_messages(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        for key in ("messages", "message"):
            value = payload.get(key)
            if isinstance(value, list) and all(isinstance(item, dict) for item in value):
                return value
        for key in ("data", "session", "result"):
            value = payload.get(key)
            found = find_messages(value)
            if found:
                return found
    return []


def text_fragments(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from text_fragments(item)
    elif isinstance(value, dict):
        part_type = str(value.get("type", "")).lower()
        if part_type in {"reasoning", "thinking"}:
            return
        if isinstance(value.get("text"), str):
            yield value["text"]
        elif isinstance(value.get("content"), str):
            yield value["content"]
        else:
            for key in ("content", "parts"):
                if key in value:
                    yield from text_fragments(value[key])


def tool_names(value: Any) -> list[str]:
    names: list[str] = []
    if isinstance(value, list):
        for item in value:
            names.extend(tool_names(item))
    elif isinstance(value, dict):
        part_type = str(value.get("type", "")).lower()
        if part_type in {"tool", "tool_use", "tool-use", "tool_call", "tool-call"}:
            name = first(value, "name", "tool", "toolName", "tool_name")
            if name:
                names.append(str(name))
        for key in ("parts", "content"):
            if key in value:
                names.extend(tool_names(value[key]))
    return list(dict.fromkeys(names))


def normalize_message(message: dict[str, Any], max_chars: int) -> dict[str, Any]:
    info = message.get("info") if isinstance(message.get("info"), dict) else {}
    role = first(message, "role", "author") or first(info, "role", "author") or "unknown"
    source = message.get("parts", message.get("content", message))
    text = "\n".join(fragment.strip() for fragment in text_fragments(source) if fragment.strip())
    truncated = len(text) > max_chars
    if truncated:
        text = text[:max_chars] + "\n...[truncated]"
    error = first(message, "error") or first(info, "error")
    result: dict[str, Any] = {
        "role": str(role),
        "text": text,
        "tools": tool_names(source),
    }
    if truncated:
        result["truncated"] = True
    if error:
        result["error"] = str(error)[:1000]
    return result


def normalize_export(row: dict[str, Any], payload: Any, max_chars: int) -> dict[str, Any]:
    messages = [normalize_message(item, max_chars) for item in find_messages(payload)]
    messages = [item for item in messages if item["text"] or item["tools"] or item.get("error")]
    user_turns = sum(1 for item in messages if item["role"] == "user")
    assistant_turns = sum(1 for item in messages if item["role"] == "assistant")
    return {
        "id": session_id(row),
        "title": first(row, "title", "name", "summary"),
        "project": row_project(row),
        "updated": row_time(row),
        "metrics": {
            "messages": len(messages),
            "user_turns": user_turns,
            "assistant_turns": assistant_turns,
            "tool_calls_observed": sum(len(item["tools"]) for item in messages),
            "errors_observed": sum(1 for item in messages if item.get("error")),
        },
        "messages": messages,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-count", type=int, default=30, choices=range(1, 101), metavar="1..100")
    parser.add_argument("--project", help="Keep only sessions whose recorded project path exactly matches this path")
    parser.add_argument("--since-days", type=int, help="Keep sessions updated within this many days")
    parser.add_argument("--max-chars-per-message", type=int, default=4000)
    parser.add_argument("--output", default="-", help="Output JSON path, or - for stdout")
    parser.add_argument("--opencode", default="opencode", help="OpenCode executable name or path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.max_chars_per_message < 200:
        raise SystemExit("--max-chars-per-message must be at least 200")
    if shutil.which(args.opencode) is None and not Path(args.opencode).is_file():
        raise SystemExit(f"OpenCode executable not found: {args.opencode}")

    listed = run_json([args.opencode, "session", "list", "--max-count", str(args.max_count), "--format", "json"])
    rows = session_rows(listed)
    cutoff = None
    if args.since_days is not None:
        if args.since_days < 1:
            raise SystemExit("--since-days must be positive")
        cutoff = dt.datetime.now(tz=dt.timezone.utc) - dt.timedelta(days=args.since_days)

    selected: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    for row in rows:
        identifier = session_id(row)
        if not identifier:
            skipped.append({"id": "unknown", "reason": "missing session id"})
            continue
        if not path_matches(row_project(row), args.project):
            continue
        updated = parse_time(row_time(row))
        if cutoff is not None and (updated is None or updated < cutoff):
            continue
        try:
            exported = run_json([args.opencode, "export", identifier, "--sanitize"])
            selected.append(normalize_export(row, exported, args.max_chars_per_message))
        except RuntimeError as exc:
            skipped.append({"id": identifier, "reason": str(exc)})

    corpus = {
        "schema_version": 1,
        "generated_at": dt.datetime.now(tz=dt.timezone.utc).isoformat(),
        "collection": {
            "requested_max_count": args.max_count,
            "project_filter": str(Path(args.project).expanduser().resolve()) if args.project else None,
            "since_days": args.since_days,
            "sanitize_required": True,
            "sessions_collected": len(selected),
            "sessions_skipped": skipped,
        },
        "sessions": selected,
    }
    rendered = json.dumps(corpus, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(rendered)
    else:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Collected {len(selected)} sanitized sessions in {output}", file=sys.stderr)
    return 0 if selected else 2


if __name__ == "__main__":
    raise SystemExit(main())
