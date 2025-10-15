#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate mnemonics for Chinese radicals."""

from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Tuple

from mnemonic_common import (
    OpenAI,
    append_rows_csv,
    chat_call,
    init_openai_client,
    load_done_keys,
    load_env,
    parse_tagged_response,
    pd,
    simple_meaning,
    tqdm,
)


def radical_prompt(radical: str, meaning: str, usage_count: int) -> Tuple[str, str]:
    system = (
        "You are a creative Chinese teacher who writes quick mnemonic stories for radicals. "
        "Keep outputs under 70 words and focus on meanings modern learners will remember."
    )
    user = (
        f"Radical: {radical}\n"
        f"Meaning: {meaning or 'n/a'}\n"
        f"Usage count (approximate): {usage_count}\n"
        "Write a short, memorable story that teaches the meaning. "
        "Return text tagged like 'Meaning: ...' and 'Usage: ...' if helpful."
    )
    return system, user


def generate_radical_row(
    client: Optional[OpenAI],
    model: str,
    rate_delay: float,
    row: pd.Series,
) -> Dict[str, Any]:
    radical = row["radical"]
    meaning = simple_meaning(row.get("meaning", ""))
    usage_count = int(row.get("usage_count", 0))
    level = row.get("level", 0)

    if client is None:
        meaning_mnemonic = f"[Placeholder] {radical} = {meaning}"
    else:
        system, user = radical_prompt(radical, meaning, usage_count)
        content = chat_call(client, model, system, user, max_tokens=220, effort="minimal")
        meaning_text, _, usage = parse_tagged_response(content)
        if usage:
            meaning_text = f"{meaning_text} | Usage: {usage}"
        meaning_mnemonic = meaning_text
        time.sleep(rate_delay)

    return {
        "radical": radical,
        "meaning": meaning,
        "usage_count": usage_count,
        "level": level,
        "openai_meaning_mnemonic": meaning_mnemonic,
    }


def run(args, client: Optional[OpenAI] = None) -> Optional[OpenAI]:
    load_env()
    df = pd.read_csv(args.radicals)
    if args.test_mode:
        df = df.head(5).copy()

    done = load_done_keys(args.out, "radical") if args.resume else set()
    to_process: List[pd.Series] = [row for _, row in df.iterrows() if str(row["radical"]) not in done]

    print(f"Total radicals loaded: {len(df)}")
    if done:
        print(f"Skipping {len(done)} already generated entries.")

    if not to_process:
        print("Nothing to generate.")
        return client

    local_client = client if (client or args.dry_run) else init_openai_client()
    if not args.dry_run and local_client is None:
        print("No API client available. Running in dry-run mode.")

    header_written = os.path.exists(args.out)

    worker_count = max(1, args.workers)
    print(f"Generating {len(to_process)} radical mnemonics using {worker_count} worker(s).")
    futures = []
    with ThreadPoolExecutor(max_workers=worker_count) as pool:
        for _, row in enumerate(to_process):
            futures.append(pool.submit(generate_radical_row, local_client, args.model, args.rate_delay, row))

        batch: List[Dict[str, Any]] = []
        errors = 0
        with tqdm(total=len(to_process), desc="Radicals", unit="radical") as progress:
            for fut in as_completed(futures):
                try:
                    result = fut.result(timeout=180)
                except Exception as exc:
                    errors += 1
                    result = {
                        "radical": "?",
                        "meaning": "",
                        "usage_count": 0,
                        "level": 0,
                        "openai_meaning_mnemonic": f"Error: {exc}",
                    }
                batch.append(result)
                progress.update(1)
                if len(batch) >= args.batch_size or progress.n == len(to_process):
                    append_rows_csv(args.out, batch, header=(not header_written))
                    header_written = True
                    batch = []

    print(f"Finished radicals. Errors: {errors}")
    print(f"Output written to {args.out}")
    return local_client
