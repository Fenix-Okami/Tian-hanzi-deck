#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate mnemonics for vocabulary entries."""

from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

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


def vocab_prompt(word: str, meaning: str, pinyin: str, breakdown: str, hsk_level: int) -> tuple[str, str]:
    system = (
        "You are a creative Chinese teacher who writes short mnemonics for vocabulary words. "
        "Keep the tone practical and student-friendly while staying extremely concise (one or two short sentences per section)."
    )
    user = (
        "Create two mnemonics for this Chinese word.\n\n"
        f"Word: {word}\n"
        f"Meaning gloss options: {meaning}\n"
        f"Pronunciation: {pinyin}\n"
        f"Character Breakdown: {breakdown or 'n/a'}\n"
        f"HSK Level: {hsk_level}\n\n"
        "Provide:\n"
        "First pick the most common everyday sense from the gloss list and use it consistently.\n"
        "MEANING: No more than two crisp sentences.\n"
        "READING: One tight sentence.\n"
        "USAGE: One short usage idea.\n"
        "Format exactly as:\n"
        "MEANING: ...\n"
        "READING: ...\n"
        "USAGE: ..."
    )
    return system, user


def generate_vocab_row(
    client: Optional[OpenAI],
    model: str,
    rate_delay: float,
    row: pd.Series,
    hanzi_map: Dict[str, str],
    debug: bool = False,
) -> Dict[str, str]:
    word = row["word"]
    pinyin = row["pinyin"]
    meaning = simple_meaning(row.get("meaning", ""))
    hsk_level = int(row.get("hsk_level", 0))
    level = row.get("level", 0)

    parts = [f"{char} ({hanzi_map.get(char, char)})" for char in str(word)]
    breakdown = " + ".join(parts)

    if client is None:
        meaning_mnemonic = f"[Placeholder] {word} = {meaning}"
        reading_mnemonic = f"[Placeholder] pronounced {pinyin}"
    else:
        system, user = vocab_prompt(word, meaning, pinyin, breakdown, hsk_level)
        content = chat_call(client, model, system, user, max_tokens=220, effort="minimal", debug=debug)
        if debug:
            print(f"\n[DEBUG] Raw response for vocab {word}: {content}")
        meaning_mnemonic, reading_mnemonic, usage = parse_tagged_response(content)
        if usage:
            meaning_mnemonic = f"{meaning_mnemonic} | Usage: {usage}"
        time.sleep(rate_delay)

    return {
        "word": word,
        "pinyin": pinyin,
        "meaning": meaning,
        "hanzi_breakdown": breakdown,
        "hsk_level": hsk_level,
        "level": level,
        "openai_meaning_mnemonic": meaning_mnemonic,
        "openai_reading_mnemonic": reading_mnemonic,
    }


def build_hanzi_map(path: str) -> Dict[str, str]:
    df = pd.read_csv(path)
    return {str(row["hanzi"]): simple_meaning(row.get("meaning", "")) for _, row in df.iterrows()}


def run(args, client: Optional[OpenAI] = None) -> Optional[OpenAI]:
    load_env()
    df = pd.read_csv(args.vocab)
    if args.test_mode:
        df = df.head(5).copy()

    hanzi_map = build_hanzi_map(args.hanzi)
    done = load_done_keys(args.out, "word") if args.resume else set()
    to_process: List[pd.Series] = [row for _, row in df.iterrows() if str(row["word"]) not in done]

    print(f"Total vocabulary entries loaded: {len(df)}")
    if done:
        print(f"Skipping {len(done)} already generated entries.")

    if not to_process:
        print("Nothing to generate.")
        return client

    local_client = client if (client or args.dry_run) else init_openai_client()
    if not args.dry_run and local_client is None:
        print("No API client available. Running in dry-run mode.")

    existing_file = os.path.exists(args.out)
    header_written = existing_file
    worker_count = max(1, args.workers)

    print(f"Generating {len(to_process)} vocabulary mnemonics using {worker_count} worker(s).")
    futures = []
    with ThreadPoolExecutor(max_workers=worker_count) as pool:
        for _, row in enumerate(to_process):
            futures.append(
                pool.submit(
                    generate_vocab_row,
                    local_client,
                    args.model,
                    args.rate_delay,
                    row,
                    hanzi_map,
                    args.test_mode,
                )
            )

        batch: List[Dict[str, str]] = []
        errors = 0
        with tqdm(total=len(to_process), desc="Vocabulary", unit="word") as progress:
            for fut in as_completed(futures):
                try:
                    result = fut.result(timeout=180)
                except Exception as exc:
                    errors += 1
                    result = {
                        "word": "?",
                        "pinyin": "",
                        "meaning": "",
                        "hanzi_breakdown": "",
                        "hsk_level": 0,
                        "level": 0,
                        "openai_meaning_mnemonic": f"Error: {exc}",
                        "openai_reading_mnemonic": f"Error: {exc}",
                    }
                batch.append(result)
                progress.update(1)
                if len(batch) >= args.batch_size or progress.n == len(to_process):
                    append_rows_csv(args.out, batch, header=(not header_written))
                    header_written = True
                    batch = []

    print(f"Finished vocabulary. Errors: {errors}")
    print(f"Output written to {args.out}")
    return local_client
