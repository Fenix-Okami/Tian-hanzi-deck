#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate mnemonics for vocabulary entries."""

from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple

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
        "Keep the tone practical and student-friendly while staying extremely concise."
    )
    user = (
        "Create mnemonics for this Chinese word.\n\n"
        f"Word: {word}\n"
        f"Meaning gloss options: {meaning}\n"
        f"Pronunciation: {pinyin}\n"
        f"Character Breakdown: {breakdown or 'n/a'}\n"
        f"HSK Level: {hsk_level}\n\n"
        "Choose the most common everyday sense from the gloss list and use it throughout.\n"
        "Format exactly as:\n"
        "MEANING: <concise everyday sense>\n"
        "USAGE: <short description of how the word is used in Mandarin>\n"
        "Do not include any other sections."
    )
    return system, user


def generate_vocab_row(
    client: Optional[OpenAI],
    model: str,
    rate_delay: float,
    row: pd.Series,
    hanzi_meanings: Dict[str, str],
    hanzi_levels: Dict[str, int],
    debug: bool = False,
) -> Dict[str, str]:
    word = row["word"]
    pinyin = row["pinyin"]
    base_meaning = simple_meaning(row.get("meaning", ""))
    hsk_level = int(row.get("hsk_level", 0))

    try:
        level = int(row.get("level", 0))
    except (TypeError, ValueError):
        level = 0

    tian_level_raw = row.get("tian_level", None)
    try:
        tian_level = int(tian_level_raw)
    except (TypeError, ValueError):
        tian_level = None

    parts: List[str] = []
    char_levels: List[int] = []
    for char in str(word):
        meaning_hint = hanzi_meanings.get(char)
        if meaning_hint:
            parts.append(f"{char} ({meaning_hint})")
        char_level = hanzi_levels.get(char)
        if isinstance(char_level, int):
            char_levels.append(char_level)
    breakdown = " + ".join(parts) if parts else " + ".join(list(str(word)))

    if tian_level is None:
        if char_levels:
            tian_level = max(char_levels)
        else:
            tian_level = level

    usage_mnemonic = ""
    meaning_candidate = base_meaning

    if client is None:
        usage_mnemonic = "[Placeholder] usage description not generated"
    else:
        system, user = vocab_prompt(word, base_meaning, pinyin, breakdown, hsk_level)
        content = chat_call(client, model, system, user, max_tokens=220, effort="minimal", debug=debug)
        if debug:
            print(f"\n[DEBUG] Raw response for vocab {word}: {content}")
        parsed_meaning, _, usage = parse_tagged_response(content)
        meaning_candidate = parsed_meaning or base_meaning
        usage_mnemonic = usage or ""
        time.sleep(rate_delay)

    meaning_value = simple_meaning(meaning_candidate or base_meaning) or base_meaning
    usage_value = usage_mnemonic.strip()

    return {
        "word": word,
        "pinyin": pinyin,
        "meaning": meaning_value,
        "hanzi_breakdown": breakdown,
        "hsk_level": hsk_level,
        "level": level,
        "tian_level": tian_level,
        "description": usage_value,
    }


def build_hanzi_lookup(path: str) -> Tuple[Dict[str, str], Dict[str, int]]:
    if not os.path.exists(path):
        return {}, {}
    df = pd.read_csv(path)
    if "hanzi" not in df.columns:
        return {}, {}
    df = df.dropna(subset=["hanzi"])
    df = df.drop_duplicates(subset=["hanzi"], keep="last")

    meaning_map: Dict[str, str] = {}
    level_map: Dict[str, int] = {}

    for _, row in df.iterrows():
        hanzi = str(row["hanzi"])
        meaning_text = row.get("meaning", "")
        if isinstance(meaning_text, str):
            meaning_text = meaning_text.strip()
        if meaning_text:
            meaning_map[hanzi] = meaning_text

        level_value = row.get("tian_level", row.get("level"))
        try:
            level_int = int(level_value)
        except (TypeError, ValueError):
            level_int = None
        if level_int is not None:
            level_map[hanzi] = level_int

    return meaning_map, level_map


def run(args, client: Optional[OpenAI] = None) -> Optional[OpenAI]:
    load_env()
    df = pd.read_csv(args.vocab)
    if args.test_mode:
        df = df.head(5).copy()

    hanzi_source = getattr(args, "hanzi_mnemonic", None) or args.hanzi
    hanzi_meanings, hanzi_levels = build_hanzi_lookup(hanzi_source)
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
                    hanzi_meanings,
                    hanzi_levels,
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
                        "tian_level": 0,
                        "description": f"Error: {exc}",
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

