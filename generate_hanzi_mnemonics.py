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
        "You are a creative but phonetically accurate Chinese teacher designing micro-length mnemonics "
        "for spaced repetition decks. Your job is to make learners remember both the *meaning* (via components) "
        "and the *pronunciation* (via pinyin). Be vivid, brief (1–2 short sentences per field), and always correct. "
        "Avoid meta explanations—use image, story, or feeling instead."
    )

    comp_text = (
        ", ".join([f"{comp} ({name})" for comp, name in components_list])
        if components_list
        else "none"
    )

    user = (
        "Create two mnemonics for this Chinese character.\n\n"
        f"Character: {hanzi}\n"
        f"Meaning gloss options: {meaning}\n"
        f"Pinyin: {pinyin}\n"
        f"Components: {comp_text}\n"
        f"HSK Level: {hsk_level}\n\n"
        "1. Choose the most common everyday sense from the gloss list.\n"
        "2. Use the components to create a short, image-rich story that evokes that sense.\n"
        "3. For the reading mnemonic, do **both** of the following:\n"
        "   • Describe the English-like sound that best approximates the pinyin (focus on tricky initials).\n"
        "   • Include an emotion or gesture matching the tone pattern.\n\n"
        "Phonetic hints for tricky initials:\n"
        "   - j / q / x: like a soft 'chee' or 'shee' sound, tongue near the front\n"
        "   - zh / ch / sh / r: tongue curled back; r sounds like the 's' in 'measure'\n"
        "   - z / c / s: crisp 'ds', 'ts', 's' sounds\n"
        "   - ü (ju, qu, xu, lü, nü): say 'ee' but round your lips like 'oo'\n\n"
        "Tone emotion guide:\n"
        "   1st tone = steady or high (calm, flat)\n"
        "   2nd tone = rising (surprised, curious)\n"
        "   3rd tone = dipping (thoughtful, doubtful)\n"
        "   4th tone = falling (sharp, firm)\n\n"
        "Return valid JSON:\n"
        "{\n"
        '  \"keyword\": \"<one lowercase English word capturing the main sense>\",\n'
        '  \"meaning_mnemonic\": \"<1–2 short sentences using the components>\",\n'
        '  \"reading_mnemonic\": \"<1 short sentence linking the approximate English sound and tone to the meaning>\"\n'
        "}\n\n"
        "Example:\n"
        "{\n"
        '  \"keyword\": \"origin\",\n'
        '  \"meaning_mnemonic\": \"Two strokes lean like walking legs — one figure in motion: a person.\",\n'
        '  \"reading_mnemonic\": \"The sound *rén* starts with a soft "rzh"—you spot someone and ask, rising with surprise, ‘rén?’\"\n'
        "}"
    )
    return system, user


def generate_hanzi_row(
    client: Optional[OpenAI],
    model: str,
    rate_delay: float,
    row: pd.Series,
    radical_map: Dict[str, str],
    debug: bool = False,
) -> Dict[str, Any]:
    hanzi = row["hanzi"]
    pinyin = row["pinyin"]
    meaning_gloss = simple_meaning(row.get("meaning", ""))
    components_str = row.get("components", "")
    hsk_level = int(row.get("hsk_level", 0))
    level = row.get("tian_level", row.get("level", 0))

    if pd.isna(components_str):
        components_str = ""

    components_list: List[Tuple[str, str]] = []
    if isinstance(components_str, str) and components_str:
        for comp in components_str.split("|"):
            comp = comp.strip()
            if comp and comp.lower() != "nan":
                components_list.append((comp, radical_map.get(comp, comp)))
    if not components_list and hanzi in radical_map:
        components_list.append((hanzi, radical_map.get(hanzi, hanzi)))

    def extract_keyword(text: str) -> str:
        tokens = re.findall(r"[A-Za-z]+", text or "")
        if tokens:
            return tokens[0].lower()
        if text and text.strip():
            return text.strip().split()[0].lower()
        return hanzi.lower()

    if client is None:
        meaning_mnemonic = f"[Placeholder] {hanzi} = {meaning_gloss}"
        reading_mnemonic = f"[Placeholder] pronounced {pinyin}"
        keyword = extract_keyword(meaning_gloss)
    else:
        system, user = hanzi_prompt(hanzi, meaning_gloss, pinyin, components_list, hsk_level)
        content = chat_call(client, model, system, user, max_tokens=2000, effort="low", debug=debug)
        if debug:
            print(f"\n[DEBUG] Raw response for {hanzi}: {content}")

        keyword = ""
        try:
            cleaned = re.sub(r"^```json\s*|\s*```$", "", content.strip(), flags=re.MULTILINE)
            payload = json.loads(cleaned)
            keyword = (payload.get("keyword", "") or "").strip().lower()
            meaning_mnemonic = payload.get("meaning_mnemonic", "")
            reading_mnemonic = payload.get("reading_mnemonic", "")
        except json.JSONDecodeError:
            meaning_mnemonic, reading_mnemonic, _ = parse_tagged_response(content)
            keyword = ""

        if not keyword:
            keyword = extract_keyword(meaning_gloss)
        meaning_mnemonic = meaning_mnemonic or f"[Placeholder] {hanzi} = {meaning_gloss}"
        reading_mnemonic = reading_mnemonic or f"[Placeholder] pronounced {pinyin}"
        time.sleep(rate_delay)

    meaning_keyword = keyword or extract_keyword(meaning_gloss)

    components_out = components_str if components_str else "|".join(comp for comp, _ in components_list)

    return {
        "hanzi": hanzi,
        "pinyin": pinyin,
        "meaning": meaning_keyword,
        "components": components_out,
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
            futures.append(
                pool.submit(
                    generate_hanzi_row,
                    local_client,
                    args.model,
                    args.rate_delay,
                    row,
                    radical_map,
                    args.test_mode,
                )
            )

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
