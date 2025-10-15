#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate mnemonics for individual hanzi."""

from __future__ import annotations

import json
import os
import re
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


def hanzi_prompt(
    hanzi: str,
    meaning: str,
    pinyin: str,
    components_list: List[Tuple[str, str]],
    hsk_level: int,
) -> Tuple[str, str]:
    system = (
        "You are a creative Chinese teacher making short, vivid mnemonics in the style of spaced repetition decks. "
        "Keep outputs concise, memorable, and tied to the components provided."
    )
    comp_text = ", ".join([f"{comp} ({name})" for comp, name in components_list]) if components_list else "none"
    user = (
        "Create two mnemonics for this Chinese character.\n\n"
        f"Character: {hanzi}\n"
        f"Meaning: {meaning}\n"
        f"Pronunciation: {pinyin}\n"
        f"Components: {comp_text}\n"
        f"HSK Level: {hsk_level}\n\n"
        "Generate two entries:\n"
        "1. MEANING MNEMONIC: 2-3 sentences linking the components to the meaning.\n"
        "2. READING MNEMONIC: 1-2 sentences helping remember the sound.\n"
        "Respond with JSON like {\"meaning_mnemonic\": \"...\", \"reading_mnemonic\": \"...\"}."
    )
    return system, user


def generate_hanzi_row(
    client: Optional[OpenAI],
    model: str,
    rate_delay: float,
    row: pd.Series,
    radical_map: Dict[str, str],
) -> Dict[str, Any]:
    hanzi = row["hanzi"]
    pinyin = row["pinyin"]
    meaning = simple_meaning(row.get("meaning", ""))
    components_str = row.get("components", "")
    hsk_level = int(row.get("hsk_level", 0))
    level = row.get("tian_level", row.get("level", 0))

    components_list: List[Tuple[str, str]] = []
    if isinstance(components_str, str) and components_str:
        for comp in components_str.split("|"):
            comp = comp.strip()
            if comp:
                components_list.append((comp, radical_map.get(comp, comp)))

    if client is None:
        meaning_mnemonic = f"[Placeholder] {hanzi} = {meaning}"
        reading_mnemonic = f"[Placeholder] pronounced {pinyin}"
    else:
        system, user = hanzi_prompt(hanzi, meaning, pinyin, components_list, hsk_level)
        content = chat_call(client, model, system, user, max_tokens=240, effort="minimal")

        try:
            cleaned = re.sub(r"^```json\s*|\s*```$", "", content.strip(), flags=re.MULTILINE)
            payload = json.loads(cleaned)
            meaning_mnemonic = payload.get("meaning_mnemonic", "")
            reading_mnemonic = payload.get("reading_mnemonic", "")
        except json.JSONDecodeError:
            meaning_mnemonic, reading_mnemonic, _ = parse_tagged_response(content)

        time.sleep(rate_delay)

    return {
        "hanzi": hanzi,
        "pinyin": pinyin,
        "meaning": meaning,
        "components": components_str,
        "hsk_level": hsk_level,
        "tian_level": level,
        "meaning_mnemonic": meaning_mnemonic,
        "reading_mnemonic": reading_mnemonic,
    }


def build_radical_map(path: str) -> Dict[str, str]:
    df = pd.read_csv(path)
    return {str(row["radical"]): simple_meaning(row.get("meaning", "")) for _, row in df.iterrows()}


def run(args, client: Optional[OpenAI] = None) -> Optional[OpenAI]:
    load_env()
    df = pd.read_csv(args.hanzi)
    if args.test_mode:
        df = df.head(5).copy()

    radical_map = build_radical_map(args.radicals)
    done = load_done_keys(args.out, "hanzi") if args.resume else set()
    to_process: List[pd.Series] = [row for _, row in df.iterrows() if str(row["hanzi"]) not in done]

    print(f"Total hanzi loaded: {len(df)}")
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

    print(f"Generating {len(to_process)} hanzi mnemonics using {worker_count} worker(s).")
    futures = []
    with ThreadPoolExecutor(max_workers=worker_count) as pool:
        for _, row in enumerate(to_process):
            futures.append(pool.submit(generate_hanzi_row, local_client, args.model, args.rate_delay, row, radical_map))

        batch: List[Dict[str, Any]] = []
        errors = 0
        with tqdm(total=len(to_process), desc="Hanzi", unit="character") as progress:
            for fut in as_completed(futures):
                try:
                    result = fut.result(timeout=240)
                except Exception as exc:
                    errors += 1
                    result = {
                        "hanzi": "?",
                        "pinyin": "",
                        "meaning": "",
                        "components": "",
                        "hsk_level": 0,
                        "tian_level": 0,
                        "meaning_mnemonic": f"Error: {exc}",
                        "reading_mnemonic": f"Error: {exc}",
                    }
                batch.append(result)
                progress.update(1)
                if len(batch) >= args.batch_size or progress.n == len(to_process):
                    append_rows_csv(args.out, batch, header=(not header_written))
                    header_written = True
                    batch = []

    print(f"Finished hanzi. Errors: {errors}")
    print(f"Output written to {args.out}")
    return local_client
