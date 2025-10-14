#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Mnemonic CSVs with OpenAI Integration (SDK + Responses API, gpt-5-mini)
- Two outputs:
  1) data/hanzi_mnemonics.csv
  2) data/vocabulary_mnemonics.csv

Retains:
- argparse flags (model, dry-run, test-mode, batch-size, workers)
- retries with exponential backoff on transient errors
- small thread pool
- caching + checkpointing
- robust parsing of model output
- simple-meaning normalizer for CEDICT-style definitions

Notes:
- Uses OpenAI Python SDK (Responses API), no raw requests
- Default model: gpt-5-mini
"""

import sys, os, io, time, re, json, argparse, csv, threading
from typing import Optional, Tuple, Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Windows console UTF-8 setup
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import pandas as pd
    from dotenv import load_dotenv
    from tqdm import tqdm
    from openai import OpenAI, APIConnectionError, APIStatusError
except ImportError as e:
    print(f"❌ Error: Required library not installed - {e}")
    print("\nTo install dependencies, run:")
    print("  pip install pandas pyarrow python-dotenv tqdm openai")
    sys.exit(1)

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Loaded environment from {env_path}")
else:
    print(f"⚠️  No .env file found at {env_path}")
    print("   You can create one from .env.example")

# ---------------------------
# Argparse / Config
# ---------------------------
def build_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="HSK Mnemonic Generator")
    p.add_argument("--model", default="gpt-5-mini", help="OpenAI model name (default: gpt-5-mini)")
    p.add_argument("--radicals", default="data/radicals_tian.csv", help="Path to radicals CSV")
    p.add_argument("--hanzi", default="data/hanzi.csv", help="Path to hanzi CSV")
    p.add_argument("--vocab", default="data/vocabulary.csv", help="Path to vocab CSV")
    p.add_argument("--out_radicals", default="data/radicals_mnemonic.csv", help="Output CSV for radicals")
    p.add_argument("--out_hanzi", default="data/hanzi_mnemonic.csv", help="Output CSV for hanzi")
    p.add_argument("--out_vocab", default="data/vocab_mnemonic.csv", help="Output CSV for vocabulary")
    p.add_argument("--batch-size", type=int, default=10, help="Progress print batch size")
    p.add_argument("--workers", type=int, default=2, help="Thread workers (1–6 safe)")
    p.add_argument("--rate-delay", type=float, default=0.4, help="Delay between calls per worker (sec)")
    p.add_argument("--dry-run", action="store_true", help="No API calls; write placeholders")
    p.add_argument("--test-mode", action="store_true", help="Only first 5 items each")
    p.add_argument("--resume", action="store_true", help="Resume from existing output CSVs (skip already done)")
    p.add_argument("--types", default="all", help="Which types to generate: 'all', 'radicals', 'hanzi', 'vocab', or comma-separated (e.g., 'hanzi,vocab')")
    return p.parse_args()

# ---------------------------
# OpenAI Client (SDK)
# ---------------------------
def init_openai_client() -> Optional[OpenAI]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        print("⚠️  OPENAI_API_KEY not set. Running in DRY RUN mode.")
        print("\nTo use OpenAI API:")
        print("  1. Get your API key from: https://platform.openai.com/api-keys")
        print("  2. Edit .env file and set: OPENAI_API_KEY=sk-your-actual-key")
        print("  3. Or export it: export OPENAI_API_KEY='sk-your-actual-key'")
        return None
    # You can also set timeout / max_retries here if desired.
    return OpenAI()

# ---------------------------
# Helpers
# ---------------------------
def backoff_delays(attempt: int) -> float:
    # exponential backoff with jitter
    base = min(2 ** attempt, 16)
    return base * (0.5 + os.urandom(1)[0] / 255)

def simple_meaning(def_str: str) -> str:
    """Keep a single learner-friendly gloss from a CEDICT-style definition."""
    if not isinstance(def_str, str) or not def_str:
        return ""
    s = re.sub(r'variant of [^;]+;?', '', def_str, flags=re.I)
    s = re.sub(r'CL:[^;]+;?', '', s, flags=re.I)
    s = s.strip().strip(';')
    s = re.split(r'[\/;()]', s)[0].strip()
    if ',' in s:
        s = s.split(',')[0].strip()
    s = re.sub(r'^[^a-zA-Z]*', '', s) or s
    return s or def_str

def parse_tagged_response(text: str) -> Tuple[str, str, str]:
    """Extract MEANING / READING / USAGE from a model response, tolerating drift."""
    meaning = reading = usage = ""
    if not text:
        return meaning, reading, usage

    for line in text.splitlines():
        L = line.strip()
        if re.match(r'^MEANING\s*:', L, flags=re.I):
            meaning = re.sub(r'^MEANING\s*:\s*', '', L, flags=re.I).strip()
        elif re.match(r'^READING\s*:', L, flags=re.I):
            reading = re.sub(r'^READING\s*:\s*', '', L, flags=re.I).strip()
        elif re.match(r'^USAGE\s*:', L, flags=re.I):
            usage = re.sub(r'^USAGE\s*:\s*', '', L, flags=re.I).strip()

    if not meaning:
        m = re.split(r'(?<=[。.!?])\s+', text.strip())
        meaning = (m[0] if m else "").strip()
    if not reading:
        m = re.search(r'(sounds like|remember.*pronunciation|rhyme|mnemonic).*', text, flags=re.I)
        if m: reading = m.group(0).strip()

    def _trim(val: str) -> str:
        return re.sub(r'^\[|\]$', '', val).strip()
    meaning, reading, usage = _trim(meaning), _trim(reading), _trim(usage)
    return meaning, reading, usage

def safe_open_mode(path: str) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path

# ---------------------------
# Responses API wrapper (SDK)
# ---------------------------
def _extract_output_text(resp) -> str:
    """
    Extract plain text from SDK Responses object.
    Prefer resp.output_text, then dig into output items if needed.
    """
    # 1) SDK convenience property
    if getattr(resp, "output_text", None):
        return resp.output_text

    # 2) Walk the generic structure
    try:
        output = getattr(resp, "output", None) or []
        for item in output:
            if getattr(item, "type", None) == "message" and getattr(item, "role", None) == "assistant":
                for part in getattr(item, "content", []) or []:
                    if getattr(part, "type", None) == "output_text":
                        text = getattr(part, "text", None)
                        if isinstance(text, str):
                            return text
                    # generic fallback for SDK model extras
                    for key in ("text", "string", "content"):
                        val = getattr(part, key, None)
                        if isinstance(val, str):
                            return val
        # summary_text fallback
        for item in output:
            if getattr(item, "type", None) == "summary_text":
                txt = getattr(item, "text", None)
                if isinstance(txt, str):
                    return txt
    except Exception:
        pass

    # 3) Last resort: stringified object
    try:
        return str(resp)
    except Exception:
        return ""

def chat_call(
    client: Optional[OpenAI],
    model: str,
    system: str,
    user: str,
    max_tokens: int = 300,
    effort: str = "minimal",   # "minimal" | "low" | "medium" | "high"
) -> str:
    if client is None:
        return "[Placeholder response]"
    attempts = 0

    while True:
        try:
            resp = client.responses.create(
                model=model,
                input=[
                    {"role": "system", "content": [{"type": "input_text", "text": system}]},
                    {"role": "user",   "content": [{"type": "input_text", "text": user}]},
                ],
                max_output_tokens=int(max_tokens),
                reasoning={"effort": effort} if effort else None,
            )
            return _extract_output_text(resp).strip()

        except (APIConnectionError,) as e:
            attempts += 1
            if attempts > 6:
                raise RuntimeError(f"API connection error after {attempts} attempts: {e}") from e
            time.sleep(backoff_delays(attempts))
        except (APIStatusError,) as e:
            status = getattr(e, "status_code", None)
            body = getattr(getattr(e, "response", None), "text", "") or ""
            # Retry on 408/409/429/5xx similarly to SDK defaults, but with our own cap.
            if status in (408, 409, 429) or (status and status >= 500):
                attempts += 1
                if attempts > 6:
                    raise RuntimeError(f"API error after {attempts} attempts: {e}\nBody: {body[:400]}") from e
                time.sleep(backoff_delays(attempts))
                continue
            # Special-case: if a model 400s on reasoning, retry once without it.
            if status == 400 and ("reasoning" in body or "effort" in body):
                if effort:
                    effort = ""  # disable and retry
                    attempts += 1
                    time.sleep(backoff_delays(attempts))
                    continue
            # Otherwise, bubble up quickly
            raise RuntimeError(f"API error: HTTP {status}\nBody: {body[:400]}") from e
        except Exception as e:
            attempts += 1
            if attempts > 3:
                raise
            time.sleep(backoff_delays(attempts))

# ---------------------------
# Prompt builders
# ---------------------------
def hanzi_prompt(hanzi: str, meaning: str, pinyin: str, components_list: List[Tuple[str, str]], hsk_level: int) -> Tuple[str, str]:
    system = ("You are a creative Chinese teacher making short, vivid mnemonics in the style of WaniKani. "
              "Keep outputs compact, memorable, and practical for flashcards. Use the component meanings to create stories.")
    comp_text = ", ".join([f"{comp} ({name})" for comp, name in components_list]) if components_list else "none"
    user = f"""Create two mnemonics for this Chinese character.

Character: {hanzi}
Meaning: {meaning}
Pronunciation: {pinyin}
Components: {comp_text}
HSK Level: {hsk_level}

Generate two creative mnemonics:
1. MEANING MNEMONIC: Create a short, memorable story (2-3 sentences) connecting the component meanings to the character's meaning. Be creative and visual.
2. READING MNEMONIC: Create a short sound association (1-2 sentences) to remember the pronunciation {pinyin}.

Respond with ONLY a JSON object in this exact format:
{{"meaning_mnemonic": "your meaning mnemonic here", "reading_mnemonic": "your reading mnemonic here"}}"""
    return system, user

def vocab_prompt(word: str, meaning: str, pinyin: str, breakdown: str, hsk_level: int) -> Tuple[str,str]:
    system = ("You are a creative Chinese teacher making short, vivid mnemonics. "
              "Keep outputs compact and practical for flashcards.")
    user = f"""Create two mnemonics for this Chinese word.

Word: {word}
Meaning: {meaning}
Pronunciation: {pinyin}
Character Breakdown: {breakdown}
HSK Level: {hsk_level}

Generate:
1. MEANING MNEMONIC: 2–3 concise sentences, optionally using character meanings.
2. READING MNEMONIC: 1–2 concise sentences using sound associations.
Also add: USAGE (1–2 short example contexts).

Format exactly:
MEANING: ...
READING: ...
USAGE: ..."""
    return system, user

def radical_prompt(radical: str, meaning: str, usage_count: int) -> Tuple[str, str]:
    system = ("You are a creative Chinese teacher making short, vivid mnemonics. "
              "Keep outputs compact and practical for flashcards.")
    user = f"""Create a mnemonic for this Chinese radical/component.

Radical: {radical}
Meaning: {meaning}
Appears in: {usage_count} characters

Generate:
1. MEANING MNEMONIC: 2–3 concise sentences with a memorable visual or story about what this component represents.
Also add: USAGE (1 sentence about its role in characters).

Format exactly:
MEANING: ...
USAGE: ..."""
    return system, user

# ---------------------------
# Workers
# ---------------------------
def generate_radical_row(client: Optional[OpenAI], model: str, rate_delay: float,
                         row: pd.Series) -> Dict[str, Any]:
    radical = row["radical"]
    meaning = simple_meaning(row.get("meaning", ""))
    usage_count = int(row.get("usage_count", 0))
    level = row.get("level", 0)

    if client is None:
        meaning_m = f"[Placeholder] {radical} = {meaning}"
    else:
        system, user = radical_prompt(radical, meaning, usage_count)
        content = chat_call(client, model, system, user, max_tokens=220, effort="minimal")
        m, r, u = parse_tagged_response(content)
        if u:
            m = f"{m} | Usage: {u}"
        meaning_m = m
        time.sleep(rate_delay)

    return {
        "radical": radical,
        "meaning": meaning,
        "usage_count": usage_count,
        "level": level,
        "openai_meaning_mnemonic": meaning_m,
    }

def generate_hanzi_row(client: Optional[OpenAI], model: str, rate_delay: float,
                       row: pd.Series, radical_map: Dict[str, str]) -> Dict[str, Any]:
    hanzi = row["hanzi"]
    pinyin = row["pinyin"]
    meaning = simple_meaning(row.get("meaning", ""))
    components_str = row.get("components", "")
    hsk_level = int(row.get("hsk_level", 0))
    level = row.get("tian_level", row.get("level", 0))

    components_list = []
    if components_str and isinstance(components_str, str):
        for comp in components_str.split("|"):
            comp = comp.strip()
            if comp:
                comp_name = radical_map.get(comp, comp)
                components_list.append((comp, comp_name))

    if client is None:
        meaning_m = f"[Placeholder] {hanzi} = {meaning}"
        reading_m = f"[Placeholder] Pronounced {pinyin}"
    else:
        try:
            system, user = hanzi_prompt(hanzi, meaning, pinyin, components_list, hsk_level)
            content = chat_call(client, model, system, user, max_tokens=240, effort="minimal")
        except Exception as e:
            raise Exception(f"API call failed for {hanzi}: {e}")

        # Try strict JSON first, then fallback
        try:
            content_clean = re.sub(r'^```json\s*|\s*```$', '', content.strip(), flags=re.MULTILINE)
            json_data = json.loads(content_clean)
            meaning_m = json_data.get("meaning_mnemonic", "")
            reading_m = json_data.get("reading_mnemonic", "")
        except json.JSONDecodeError:
            m, r, u = parse_tagged_response(content)
            meaning_m, reading_m = m, r

        time.sleep(rate_delay)

    return {
        "hanzi": hanzi,
        "pinyin": pinyin,
        "meaning": meaning,
        "components": components_str,
        "hsk_level": hsk_level,
        "tian_level": level,
        "meaning_mnemonic": meaning_m,
        "reading_mnemonic": reading_m,
    }

def generate_vocab_row(client: Optional[OpenAI], model: str, rate_delay: float,
                       row: pd.Series, hanzi_map: Dict[str, str]) -> Dict[str, Any]:
    word = row["word"]
    pinyin = row["pinyin"]
    meaning = simple_meaning(row.get("meaning", ""))
    hsk_level = int(row.get("hsk_level", 0))
    level = row.get("level", 0)

    parts = []
    for ch in word:
        parts.append(f"{ch} ({hanzi_map.get(ch, ch)})")
    breakdown = " + ".join(parts)

    if client is None:
        meaning_m = f"[Placeholder] {word} = {meaning}"
        reading_m = f"[Placeholder] Pronounced {pinyin}"
    else:
        system, user = vocab_prompt(word, meaning, pinyin, breakdown, hsk_level)
        content = chat_call(client, model, system, user, max_tokens=220, effort="minimal")
        m, r, u = parse_tagged_response(content)
        if u:
            m = f"{m} | Usage: {u}"
        meaning_m, reading_m = m, r
        time.sleep(rate_delay)

    return {
        "word": word,
        "pinyin": pinyin,
        "meaning": meaning,
        "hanzi_breakdown": breakdown,
        "hsk_level": hsk_level,
        "level": level,
        "openai_meaning_mnemonic": meaning_m,
        "openai_reading_mnemonic": reading_m,
    }

# ---------------------------
# Checkpointing / Resume
# ---------------------------
def load_done_keys(path: str, key_col: str) -> set:
    if not os.path.exists(path):
        return set()
    try:
        df = pd.read_csv(path)
        return set(df[key_col].astype(str).tolist())
    except Exception:
        return set()

def append_rows_csv(path: str, rows: List[Dict[str, Any]], header: bool):
    safe_open_mode(path)
    with open(path, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        if header:
            w.writeheader()
        w.writerows(rows)

# ---------------------------
# Main
# ---------------------------
def main():
    args = build_args()
    print("="*70)
    print("🎴 HSK Mnemonic Generator (SDK Responses API, gpt-5-mini)")
    print("="*70)

    client = None if args.dry_run else init_openai_client()
    model = args.model
    if client:
        print(f"✓ OpenAI SDK ready. Model: {model}")

        # Quick API test
        print("Testing API connection...")
        try:
            test_resp = client.responses.create(
                model=model,
                input="Reply with OK",
                max_output_tokens=16,
                reasoning={"effort": "minimal"},
            )
            test_text = _extract_output_text(test_resp)
            print(f"✓ API test successful: {test_text[:50]}")
        except Exception as e:
            print(f"❌ API test failed: {e}")
            print("Please check your API key or model name.")
            sys.exit(1)
    else:
        print("⚠️  DRY RUN mode active (placeholders only).")
    print()

    # Load data
    print("📂 Loading data ...")
    try:
        radicals_df = pd.read_csv(args.radicals)
        hanzi_df = pd.read_csv(args.hanzi)
        vocab_df = pd.read_csv(args.vocab)
        if args.test_mode:
            radicals_df = radicals_df.head(5)
            hanzi_df = hanzi_df.head(5)
            vocab_df = vocab_df.head(5)
        print(f"✓ Radicals: {len(radicals_df)} | Hanzi: {len(hanzi_df)} | Vocab: {len(vocab_df)}")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        sys.exit(1)

    # Build maps
    hanzi_map = {str(r["hanzi"]): simple_meaning(r.get("meaning","")) for _, r in hanzi_df.iterrows()}
    radical_map = {str(r["radical"]): str(r.get("meaning","")) for _, r in radicals_df.iterrows()}

    # Resume
    done_radicals = load_done_keys(args.out_radicals, "radical") if args.resume else set()
    done_hanzi = load_done_keys(args.out_hanzi, "hanzi") if args.resume else set()
    done_vocab = load_done_keys(args.out_vocab, "word") if args.resume else set()

    # Determine types
    if args.types.lower() == "all":
        types_to_gen = {"radicals", "hanzi", "vocab"}
    else:
        types_to_gen = set(t.strip().lower() for t in args.types.split(","))

    print(f"\n📋 Generating mnemonics for: {', '.join(sorted(types_to_gen))}")

    # ---------------- Radicals ----------------
    if "radicals" in types_to_gen:
        print("\n" + "="*70)
        print("🔷 Part 1: Radical Mnemonics")
        print("="*70)

        header_written_radicals = os.path.exists(args.out_radicals)

        to_process_r = [(i, r) for i, r in radicals_df.iterrows() if str(r["radical"]) not in done_radicals]
        total_r = len(to_process_r)
        print(f"→ Pending radicals: {total_r} (skipping {len(radicals_df)-total_r} already done)")

        if total_r:
            with ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
                futures = [ex.submit(generate_radical_row, client, model, args.rate_delay, row) for _, row in to_process_r]

                batch: List[Dict[str, Any]] = []
                completed = 0
                with tqdm(total=total_r, desc="Generating radical mnemonics", unit="radical") as pbar:
                    for fut in as_completed(futures):
                        try:
                            res = fut.result()
                            batch.append(res)
                        except Exception as e:
                            batch.append({
                                "radical": "?",
                                "meaning": "",
                                "usage_count": 0,
                                "level": 0,
                                "openai_meaning_mnemonic": f"Error: {e}",
                            })
                        completed += 1
                        pbar.update(1)
                        if len(batch) >= args.batch_size or completed == total_r:
                            append_rows_csv(args.out_radicals, batch, header=(not header_written_radicals))
                            header_written_radicals = True
                            batch = []

    # ---------------- Hanzi ----------------
    if "hanzi" in types_to_gen:
        print("\n" + "="*70)
        print("📝 Part 2: Hanzi Mnemonics")
        print("="*70)

        header_written_hanzi = os.path.exists(args.out_hanzi)

        to_process = [(i, r) for i, r in hanzi_df.iterrows() if str(r["hanzi"]) not in done_hanzi]
        total = len(to_process)
        print(f"→ Pending hanzi: {total} (skipping {len(hanzi_df)-total} already done)")

        if client:
            print(f"✓ OpenAI client active (model: {model})")
        else:
            print(f"⚠️  Running in DRY RUN mode (no API calls)")

        if total:
            with ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
                futures = [ex.submit(generate_hanzi_row, client, model, args.rate_delay, row, radical_map) for _, row in to_process]

                batch: List[Dict[str, Any]] = []
                completed = 0
                errors = 0
                with tqdm(total=total, desc="Generating hanzi mnemonics", unit="hanzi") as pbar:
                    for fut in as_completed(futures):
                        try:
                            res = fut.result(timeout=180)
                            batch.append(res)
                        except Exception as e:
                            errors += 1
                            if errors <= 3:
                                print(f"\n⚠️  Error generating mnemonic: {e}")
                            batch.append({
                                "hanzi": "?",
                                "pinyin": "",
                                "meaning": "",
                                "components": "",
                                "hsk_level": 0,
                                "tian_level": 0,
                                "meaning_mnemonic": f"Error: {e}",
                                "reading_mnemonic": f"Error: {e}",
                            })
                        completed += 1
                        pbar.update(1)
                        if len(batch) >= args.batch_size or completed == total:
                            append_rows_csv(args.out_hanzi, batch, header=(not header_written_hanzi))
                            header_written_hanzi = True
                            batch = []

    # ---------------- Vocabulary ----------------
    if "vocab" in types_to_gen:
        print("\n" + "="*70)
        print("📚 Part 3: Vocabulary Mnemonics")
        print("="*70)

        header_written_vocab = os.path.exists(args.out_vocab)

        to_process_v = [(i, r) for i, r in vocab_df.iterrows() if str(r["word"]) not in done_vocab]
        total_v = len(to_process_v)
        print(f"→ Pending vocab: {total_v} (skipping {len(vocab_df)-total_v} already done)")

        if total_v:
            with ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
                futures = [ex.submit(generate_vocab_row, client, model, args.rate_delay, row, hanzi_map) for _, row in to_process_v]

                batch: List[Dict[str, Any]] = []
                completed = 0
                with tqdm(total=total_v, desc="Generating vocab mnemonics", unit="word") as pbar:
                    for fut in as_completed(futures):
                        try:
                            res = fut.result()
                            batch.append(res)
                        except Exception as e:
                            batch.append({
                                "word": "?",
                                "pinyin": "",
                                "meaning": "",
                                "hanzi_breakdown": "",
                                "hsk_level": 0,
                                "level": 0,
                                "openai_meaning_mnemonic": f"Error: {e}",
                                "openai_reading_mnemonic": f"Error: {e}",
                            })
                        completed += 1
                        pbar.update(1)
                        if len(batch) >= args.batch_size or completed == total_v:
                            append_rows_csv(args.out_vocab, batch, header=(not header_written_vocab))
                            header_written_vocab = True
                            batch = []

    # Summary
    print("\n" + "="*70)
    print("✨ Mnemonic Generation Complete!")
    print("="*70)
    print(f"\n📁 Output files:")
    if "radicals" in types_to_gen:
        print(f"   🔷 {args.out_radicals}")
    if "hanzi" in types_to_gen:
        print(f"   📝 {args.out_hanzi}")
    if "vocab" in types_to_gen:
        print(f"   📚 {args.out_vocab}")

    if client:
        est_items = 0
        if "radicals" in types_to_gen and 'to_process_r' in locals():
            est_items += len(to_process_r)
        if "hanzi" in types_to_gen and 'to_process' in locals():
            est_items += len(to_process)
        if "vocab" in types_to_gen and 'to_process_v' in locals():
            est_items += len(to_process_v)
        est_tokens = est_items * 250  # trimmed outputs
        est_cost = est_tokens / 1_000_000 * 0.15
        print(f"\n💰 Rough cost estimate: ~${est_cost:.2f} (≈{est_tokens:,} tokens)")
    else:
        print("\n⚠️  Placeholders were used (DRY RUN or no API key).")

if __name__ == "__main__":
    main()
