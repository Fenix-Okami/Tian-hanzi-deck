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
    chat_call,
    init_openai_client,
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
        # Retry generation up to 5 times on parsing or API issues
        attempts = 0
        last_exc: Optional[Exception] = None
        while attempts < 5:
            attempts += 1
            try:
                system, user = hanzi_prompt(hanzi, meaning_gloss, pinyin, components_list, hsk_level)
                content = chat_call(
                    client, model, system, user, max_tokens=2000, effort="minimal", debug=debug
                )
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
                    # Try to parse simple tagged fallback
                    meaning_mnemonic, reading_mnemonic, _ = parse_tagged_response(content)
                    keyword = ""

                if not keyword:
                    keyword = extract_keyword(meaning_gloss)
                meaning_mnemonic = meaning_mnemonic or f"[Placeholder] {hanzi} = {meaning_gloss}"
                reading_mnemonic = reading_mnemonic or f"[Placeholder] pronounced {pinyin}"
                time.sleep(rate_delay)
                break
            except Exception as exc:
                last_exc = exc
                # brief linear backoff between attempts
                time.sleep(min(1.5 * attempts, 5))
        else:
            # After retries, return error markers
            meaning_mnemonic = f"Error: {last_exc}"
            reading_mnemonic = f"Error: {last_exc}"
            keyword = extract_keyword(meaning_gloss)

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


def _is_error_row(row: pd.Series) -> bool:
    """Heuristics to identify rows that failed generation earlier."""
    mm = str(row.get("meaning_mnemonic", ""))
    rm = str(row.get("reading_mnemonic", ""))
    if mm.startswith("Error:") or rm.startswith("Error:"):
        return True
    if mm.startswith("[Placeholder]") or rm.startswith("[Placeholder]"):
        return True
    return False


def run(args, client: Optional[OpenAI] = None) -> Optional[OpenAI]:
    load_env()
    df = pd.read_csv(args.hanzi)
    if args.test_mode:
        df = df.head(5).copy()

    radical_map = build_radical_map(args.radicals)
    # Load existing output rows if any
    existing_map: Dict[str, Dict[str, Any]] = {}
    if os.path.exists(args.out):
        try:
            existing_df = pd.read_csv(args.out)
            for _, r in existing_df.iterrows():
                existing_map[str(r.get("hanzi", ""))] = {k: r.get(k, "") for k in existing_df.columns}
        except Exception:
            existing_map = {}

    # Select what to process: if resume is True, process only missing or error rows; otherwise all
    to_process: List[pd.Series] = []
    if args.resume and existing_map:
        # Build set of error/missing hanzi
        existing_df = pd.DataFrame(existing_map.values()) if existing_map else pd.DataFrame()
        error_keys = set()
        if not existing_df.empty:
            error_keys = set(
                str(r["hanzi"]) for _, r in existing_df.iterrows() if _is_error_row(r)
            )
        for _, row in df.iterrows():
            key = str(row["hanzi"]) 
            if key not in existing_map or key in error_keys:
                to_process.append(row)
    else:
        to_process = [row for _, row in df.iterrows()]

    print(f"Total hanzi loaded: {len(df)}")
    skipped = len(df) - len(to_process)
    if skipped > 0:
        print(f"Skipping {skipped} already generated entries.")

    if not to_process:
        print("Nothing to generate.")
        return client

    local_client = client if (client or args.dry_run) else init_openai_client()
    if not args.dry_run and local_client is None:
        print("No API client available. Running in dry-run mode.")

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
                # Periodically merge into existing_map to avoid memory growth
                if len(batch) >= args.batch_size or progress.n == len(to_process):
                    for item in batch:
                        key = str(item.get("hanzi", ""))
                        if key and key != "?":
                            existing_map[key] = item
                    batch = []

    # Persist: rewrite file with updated rows (replace entries)
    # Preserve order of input hanzi where possible
    final_rows: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        key = str(row["hanzi"]) 
        if key in existing_map:
            final_rows.append(existing_map[key])
    # Include any extra rows previously present but not in current input (unlikely)
    input_keys = {str(row["hanzi"]) for _, row in df.iterrows()}
    for k, v in existing_map.items():
        if k not in input_keys:
            final_rows.append(v)

    out_df = pd.DataFrame(final_rows)
    out_df.to_csv(args.out, index=False, encoding="utf-8")

    print(f"Finished hanzi. Errors: {errors}")
    print(f"Output written (rewritten) to {args.out}")
    return local_client
