#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared helpers for mnemonic generation scripts."""

from __future__ import annotations

import csv
import io
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Windows console UTF-8 setup
def configure_console() -> None:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


configure_console()

try:
    import pandas as pd
    from dotenv import load_dotenv
    from tqdm import tqdm
    from openai import OpenAI, APIConnectionError, APIStatusError
except ImportError as exc:
    print(f"Dependency error: {exc}")
    print("\nInstall missing packages with:")
    print("  pip install pandas pyarrow python-dotenv tqdm openai")
    sys.exit(1)


_ENV_LOADED = False


def load_env(env_name: str = ".env") -> None:
    """Load environment variables from a local .env file."""
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    env_path = Path(__file__).parent / env_name
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded environment from {env_path}")
    else:
        print(f"Warning: no .env file found at {env_path}")
        print("         You can copy .env.example to configure local secrets.")
    _ENV_LOADED = True


def init_openai_client() -> Optional[OpenAI]:
    """Create an OpenAI client if an API key is available."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        print("Warning: OPENAI_API_KEY not set. Falling back to dry-run placeholders.")
        return None
    return OpenAI()


def backoff_delay(attempt: int) -> float:
    """Compute an exponential backoff delay with jitter."""
    base = min(2 ** attempt, 16)
    return base * (0.5 + os.urandom(1)[0] / 255)


def _extract_output_text(resp: Any) -> str:
    """Collapse the Responses API payload into plain text."""
    chunks: List[str] = []
    for item in getattr(resp, "output", []) or []:
        if item.type != "output_text":
            continue
        chunks.append(getattr(item, "text", ""))
    return "".join(chunks)


def chat_call(
    client: Optional[OpenAI],
    model: str,
    system: str,
    user: str,
    max_tokens: int = 300,
    effort: str = "minimal",
) -> str:
    """Call the OpenAI Responses API with retries."""
    if client is None:
        return "[Placeholder response]"
    attempts = 0

    while True:
        try:
            resp = client.responses.create(
                model=model,
                input=[
                    {"role": "system", "content": [{"type": "input_text", "text": system}]},
                    {"role": "user", "content": [{"type": "input_text", "text": user}]},
                ],
                max_output_tokens=int(max_tokens),
                reasoning={"effort": effort} if effort else None,
            )
            return _extract_output_text(resp).strip()

        except (APIConnectionError,) as exc:
            attempts += 1
            if attempts > 6:
                raise RuntimeError(f"API connection error after {attempts} attempts: {exc}") from exc
            time.sleep(backoff_delay(attempts))
        except (APIStatusError,) as exc:
            status = getattr(exc, "status_code", None)
            body = getattr(getattr(exc, "response", None), "text", "") or ""
            if status in (408, 409, 429) or (status and status >= 500):
                attempts += 1
                if attempts > 6:
                    raise RuntimeError(f"API error after {attempts} attempts: {exc}\nBody: {body[:400]}") from exc
                time.sleep(backoff_delay(attempts))
                continue
            if status == 400 and ("reasoning" in body or "effort" in body):
                if effort:
                    effort = ""
                    attempts += 1
                    time.sleep(backoff_delay(attempts))
                    continue
            raise RuntimeError(f"API error: HTTP {status}\nBody: {body[:400]}") from exc
        except Exception as exc:
            attempts += 1
            if attempts > 3:
                raise
            time.sleep(backoff_delay(attempts))


def simple_meaning(def_str: str) -> str:
    """Extract a short learner-friendly gloss from a CEDICT style string."""
    if not isinstance(def_str, str) or not def_str:
        return ""
    text = re.sub(r"variant of [^;]+;?", "", def_str, flags=re.I)
    text = re.sub(r"CL:[^;]+;?", "", text, flags=re.I)
    text = text.strip().strip(";")
    text = re.split(r"[\/;()]", text)[0].strip()
    if "," in text:
        text = text.split(",", 1)[0].strip()
    text = re.sub(r"^[^a-zA-Z]*", "", text) or text
    return text or def_str


def parse_tagged_response(text: str) -> Tuple[str, str, str]:
    """Extract MEANING / READING / USAGE sections from model output."""
    meaning = reading = usage = ""
    if not text:
        return meaning, reading, usage

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.lower().startswith("meaning:"):
            meaning = line.split(":", 1)[1].strip()
        elif line.lower().startswith("reading:"):
            reading = line.split(":", 1)[1].strip()
        elif line.lower().startswith("usage:"):
            usage = line.split(":", 1)[1].strip()
        elif not meaning:
            meaning = line

    return meaning, reading, usage


def safe_open_mode(path: str) -> None:
    """Ensure the parent directory for a file exists before writing."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def load_done_keys(path: str, key_col: str) -> set:
    """Load already generated keys from an output CSV."""
    if not os.path.exists(path):
        return set()
    try:
        df = pd.read_csv(path)
        return set(df[key_col].astype(str).tolist())
    except Exception:
        return set()


def append_rows_csv(path: str, rows: List[Dict[str, Any]], header: bool) -> None:
    """Append a batch of rows to a CSV file."""
    safe_open_mode(path)
    with open(path, "a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        if header:
            writer.writeheader()
        writer.writerows(rows)
