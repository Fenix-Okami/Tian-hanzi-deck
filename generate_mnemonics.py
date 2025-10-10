#!/usr/bin/env python3
"""
Generate Mnemonic CSVs with OpenAI Integration (Refined)
- Two outputs:
  1) data/hanzi_mnemonics.csv
  2) data/vocabulary_mnemonics.csv

Key improvements:
- argparse flags (model, dry-run, test-mode, batch-size, workers)
- retries with exponential backoff on transient errors
- small thread pool (default 1; bump to 2–4 if you must)
- caching + checkpointing
- robust parsing of model output
- simple-meaning normalizer for CEDICT-style definitions
"""

import sys, os, io, time, re, json, argparse, csv, math, threading
from typing import Optional, Tuple, Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed

# Windows console UTF-8 setup
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import pandas as pd
    from openai import OpenAI
    from openai import APIError, RateLimitError, APITimeoutError
except ImportError as e:
    print(f"❌ Error: Required library not installed - {e}")
    print("\nTo install dependencies, run:")
    print("  pip install pandas pyarrow openai")
    sys.exit(1)

# ---------------------------
# Argparse / Config
# ---------------------------
def build_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="HSK Mnemonic Generator")
    p.add_argument("--model", default="gpt-4o-mini", help="OpenAI model name")
    p.add_argument("--radicals", default="data/radicals.parquet", help="Path to radicals parquet")
    p.add_argument("--hanzi", default="data/hanzi.parquet", help="Path to hanzi parquet")
    p.add_argument("--vocab", default="data/vocabulary.parquet", help="Path to vocab parquet")
    p.add_argument("--out_radicals", default="data/radicals_mnemonics.csv", help="Output CSV for radicals")
    p.add_argument("--out_hanzi", default="data/hanzi_mnemonics.csv", help="Output CSV for hanzi")
    p.add_argument("--out_vocab", default="data/vocabulary_mnemonics.csv", help="Output CSV for vocabulary")
    p.add_argument("--batch-size", type=int, default=10, help="Progress print batch size")
    p.add_argument("--workers", type=int, default=1, help="Thread workers (1 recommended; 2-4 max)")
    p.add_argument("--rate-delay", type=float, default=0.8, help="Delay between calls per worker (sec)")
    p.add_argument("--dry-run", action="store_true", help="No API calls; write placeholders")
    p.add_argument("--test-mode", action="store_true", help="Only first 5 items each")
    p.add_argument("--resume", action="store_true", help="Resume from existing output CSVs (skip already done)")
    return p.parse_args()

# ---------------------------
# OpenAI Client
# ---------------------------
def init_openai_client() -> Optional[OpenAI]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set. Running in DRY RUN mode.")
        return None
    try:
        return OpenAI(api_key=api_key)
    except Exception as e:
        print(f"❌ Error initializing OpenAI client: {e}")
        return None

# ---------------------------
# Helpers
# ---------------------------
TEMPERATURE_SUPPORTED_CACHE: Dict[str, bool] = {}
TEMPERATURE_LOCK = threading.Lock()

def model_supports_temperature(client: OpenAI, model: str) -> bool:
    # Cache result to avoid pinging repeatedly
    with TEMPERATURE_LOCK:
        if model in TEMPERATURE_SUPPORTED_CACHE:
            return TEMPERATURE_SUPPORTED_CACHE[model]
    # Heuristic: some models reject temperature in responses API, some in chat
    # Try a tiny call without temperature first; if that works, try with temperature
    try:
        client.chat.completions.create(
            model=model,
            messages=[{"role":"user","content":"Reply with 'ok'."}],
            max_tokens=5
        )
        try:
            client.chat.completions.create(
                model=model,
                messages=[{"role":"user","content":"Reply with 'ok'."}],
                max_tokens=5,
                temperature=0.2
            )
            supported = True
        except APIError as e:
            # If error mentions temperature unsupported
            msg = str(e)
            supported = ("Unsupported parameter: 'temperature'" not in msg)
        except Exception:
            supported = True  # default assume OK unless explicit error
    except Exception:
        # If even the basic call fails, assume no temperature support to be safe
        supported = False
    with TEMPERATURE_LOCK:
        TEMPERATURE_SUPPORTED_CACHE[model] = supported
    return supported

def backoff_delays(attempt: int) -> float:
    # exponential backoff with jitter
    base = min(2 ** attempt, 32)
    return base * (0.5 + os.urandom(1)[0] / 255)

def simple_meaning(def_str: str) -> str:
    """Keep a single learner-friendly gloss from a CEDICT-style definition."""
    if not isinstance(def_str, str) or not def_str:
        return ""
    s = re.sub(r'variant of [^;]+;?', '', def_str, flags=re.I)
    s = re.sub(r'CL:[^;]+;?', '', s, flags=re.I)
    s = s.strip().strip(';')
    # Keep content before the first slash or semicolon or parentheses
    s = re.split(r'[\/;()]', s)[0].strip()
    # If multiple comma-separated, keep first short token
    if ',' in s:
        s = s.split(',')[0].strip()
    # Some entries put notes like "archaic" first—fallback to word within
    s = re.sub(r'^[^a-zA-Z]*', '', s) or s
    return s or def_str

def parse_tagged_response(text: str) -> Tuple[str, str, str]:
    """Extract MEANING / READING / USAGE from a model response, tolerating drift."""
    meaning = reading = usage = ""
    if not text:
        return meaning, reading, usage

    # First try labeled lines
    for line in text.splitlines():
        L = line.strip()
        if re.match(r'^MEANING\s*:', L, flags=re.I):
            meaning = re.sub(r'^MEANING\s*:\s*', '', L, flags=re.I).strip()
        elif re.match(r'^READING\s*:', L, flags=re.I):
            reading = re.sub(r'^READING\s*:\s*', '', L, flags=re.I).strip()
        elif re.match(r'^USAGE\s*:', L, flags=re.I):
            usage = re.sub(r'^USAGE\s*:\s*', '', L, flags=re.I).strip()

    # If missing, try bullet/paragraph heuristics
    if not meaning:
        # take first sentence as meaning
        m = re.split(r'(?<=[。.!?])\s+', text.strip())
        meaning = (m[0] if m else "").strip()
    if not reading:
        # search for pronunciation hint phrases
        m = re.search(r'(sounds like|remember.*pronunciation|rhyme|mnemonic).*', text, flags=re.I)
        if m: reading = m.group(0).strip()

    # Trim brackets residue
    for k in ("meaning", "reading", "usage"):
        val = locals()[k]
        val = re.sub(r'^\[|\]$', '', val).strip()
        locals()[k] = val

    return meaning, reading, usage

def safe_open_mode(path: str) -> str:
    # Create parent dir
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path

# ---------------------------
# OpenAI call wrappers
# ---------------------------
def chat_call(client: Optional[OpenAI], model: str, system: str, user: str,
              temp_ok: bool, temperature: float = 0.8, max_tokens: int = 300) -> str:
    """Do a chat.completions call with retries/backoff. Returns content string."""
    if client is None:
        return "[Placeholder response]"
    attempts = 0
    while True:
        try:
            kwargs = dict(
                model=model,
                messages=[{"role":"system","content":system},
                          {"role":"user","content":user}],
                max_tokens=max_tokens,
            )
            if temp_ok:
                kwargs["temperature"] = temperature
            resp = client.chat.completions.create(**kwargs)
            return (resp.choices[0].message.content or "").strip()
        except (RateLimitError, APITimeoutError) as e:
            attempts += 1
            if attempts > 6:
                raise
            time.sleep(backoff_delays(attempts))
        except APIError as e:
            # Some permanent errors should not be retried forever
            msg = str(e)
            if "Unsupported parameter: 'temperature'" in msg and "temperature" in kwargs:
                kwargs.pop("temperature", None)
                continue
            attempts += 1
            if attempts > 3:
                raise
            time.sleep(backoff_delays(attempts))
        except Exception:
            attempts += 1
            if attempts > 3:
                raise
            time.sleep(backoff_delays(attempts))

# ---------------------------
# Prompt builders
# ---------------------------
def hanzi_prompt(hanzi: str, meaning: str, pinyin: str, components: str, hsk_level: int) -> Tuple[str, str]:
    system = ("You are a creative Chinese teacher making short, vivid mnemonics. "
              "Keep outputs compact and practical for flashcards.")
    user = f"""Create two mnemonics for this Chinese character.

Character: {hanzi}
Meaning: {meaning}
Pronunciation: {pinyin}
Components: {components}
HSK Level: {hsk_level}

Generate:
1. MEANING MNEMONIC: 2–3 concise sentences using components if helpful.
2. READING MNEMONIC: 1–2 concise sentences using sound associations.
Also add: USAGE (1 sentence about typical use/collocations).

Format exactly:
MEANING: ...
READING: ...
USAGE: ..."""
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
def generate_radical_row(client: Optional[OpenAI], model: str, temp_ok: bool, rate_delay: float,
                         row: pd.Series) -> Dict[str, Any]:
    radical = row["radical"]
    meaning = simple_meaning(row.get("meaning", ""))
    usage_count = int(row.get("usage_count", 0))
    level = row.get("level", 0)

    if client is None:
        meaning_m = f"[Placeholder] {radical} = {meaning}"
    else:
        system, user = radical_prompt(radical, meaning, usage_count)
        content = chat_call(client, model, system, user, temp_ok=temp_ok, temperature=0.8, max_tokens=200)
        m, r, u = parse_tagged_response(content)
        # Radicals only have meaning mnemonic, but parser gives r="" if no READING tag
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

def generate_hanzi_row(client: Optional[OpenAI], model: str, temp_ok: bool, rate_delay: float,
                       row: pd.Series) -> Dict[str, Any]:
    hanzi = row["hanzi"]
    pinyin = row["pinyin"]
    meaning = simple_meaning(row.get("meaning", ""))  # simplify to 1 gloss
    components = row.get("components", "Unknown")
    hsk_level = int(row.get("hsk_level", 0))
    level = row.get("level", 0)

    if client is None:
        meaning_m = f"[Placeholder] {hanzi} = {meaning}"
        reading_m = f"[Placeholder] Pronounced {pinyin}"
    else:
        system, user = hanzi_prompt(hanzi, meaning, pinyin, components, hsk_level)
        content = chat_call(client, model, system, user, temp_ok=temp_ok, temperature=0.8, max_tokens=300)
        m, r, u = parse_tagged_response(content)
        if u:
            m = f"{m} | Usage: {u}"
        meaning_m, reading_m = m, r
        time.sleep(rate_delay)

    return {
        "hanzi": hanzi,
        "pinyin": pinyin,
        "meaning": meaning,
        "components": components,
        "hsk_level": hsk_level,
        "level": level,
        "openai_meaning_mnemonic": meaning_m,
        "openai_reading_mnemonic": reading_m,
    }

def generate_vocab_row(client: Optional[OpenAI], model: str, temp_ok: bool, rate_delay: float,
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
        content = chat_call(client, model, system, user, temp_ok=temp_ok, temperature=0.8, max_tokens=300)
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
    print("🎴 HSK Mnemonic Generator (Refined)")
    print("="*70)

    client = None if args.dry_run else init_openai_client()
    model = args.model
    if client:
        temp_ok = model_supports_temperature(client, model)
        print(f"✓ OpenAI ready. Model: {model} | temperature supported: {temp_ok}")
    else:
        temp_ok = False
        print("⚠️  DRY RUN mode active (placeholders only).")
    print()

    # Load data
    print("📂 Loading data ...")
    try:
        radicals_df = pd.read_parquet(args.radicals)
        hanzi_df = pd.read_parquet(args.hanzi)
        vocab_df = pd.read_parquet(args.vocab)
        if args.test_mode:
            radicals_df = radicals_df.head(5)
            hanzi_df = hanzi_df.head(5)
            vocab_df = vocab_df.head(5)
        print(f"✓ Radicals: {len(radicals_df)} | Hanzi: {len(hanzi_df)} | Vocab: {len(vocab_df)}")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        sys.exit(1)

    # Build map for vocab breakdowns (char -> simple meaning)
    hanzi_map = {str(r["hanzi"]): simple_meaning(r.get("meaning","")) for _, r in hanzi_df.iterrows()}

    # Resume support (skip already generated)
    done_radicals = load_done_keys(args.out_radicals, "radical") if args.resume else set()
    done_hanzi = load_done_keys(args.out_hanzi, "hanzi") if args.resume else set()
    done_vocab = load_done_keys(args.out_vocab, "word") if args.resume else set()

    # ---------------- Radicals ----------------
    print("\n" + "="*70)
    print("🔷 Part 1: Radical Mnemonics")
    print("="*70)

    if not os.path.exists(args.out_radicals):
        header_written_radicals = False
    else:
        header_written_radicals = True

    to_process_r = [(i, r) for i, r in radicals_df.iterrows() if str(r["radical"]) not in done_radicals]
    total_r = len(to_process_r)
    print(f"→ Pending radicals: {total_r} (skipping {len(radicals_df)-total_r} already done)")

    if total_r:
        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
            futures = []
            for i, row in to_process_r:
                futures.append(ex.submit(generate_radical_row, client, model, temp_ok, args.rate_delay, row))

            batch = []
            completed = 0
            for fut in as_completed(futures):
                try:
                    res = fut.result()
                    batch.append(res)
                except Exception as e:
                    # Write a stub row on error so we can inspect later
                    res = {
                        "radical": str(row.get("radical","?")),
                        "meaning": simple_meaning(str(row.get("meaning",""))),
                        "usage_count": int(row.get("usage_count",0)),
                        "level": row.get("level",0),
                        "openai_meaning_mnemonic": f"Error: {e}",
                    }
                    batch.append(res)

                completed += 1
                if len(batch) >= args.batch_size or completed == total_r:
                    # Append checkpoint
                    append_rows_csv(args.out_radicals, batch, header=(not header_written_radicals))
                    header_written_radicals = True
                    print(f"  ✓ Checkpoint: {completed}/{total_r} radicals")
                    batch = []

    # ---------------- Hanzi ----------------
    print("\n" + "="*70)
    print("📝 Part 2: Hanzi Mnemonics")
    print("="*70)

    # Prepare output headers if creating new
    if not os.path.exists(args.out_hanzi):
        header_written_hanzi = False
    else:
        header_written_hanzi = True

    to_process = [(i, r) for i, r in hanzi_df.iterrows() if str(r["hanzi"]) not in done_hanzi]
    total = len(to_process)
    print(f"→ Pending hanzi: {total} (skipping {len(hanzi_df)-total} already done)")

    if total:
        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
            futures = []
            for i, row in to_process:
                futures.append(ex.submit(generate_hanzi_row, client, model, temp_ok, args.rate_delay, row))

            batch = []
            completed = 0
            for fut in as_completed(futures):
                try:
                    res = fut.result()
                    batch.append(res)
                except Exception as e:
                    # Write a stub row on error so we can inspect later
                    res = {
                        "hanzi": str(row.get("hanzi","?")),
                        "pinyin": str(row.get("pinyin","")),
                        "meaning": simple_meaning(str(row.get("meaning",""))),
                        "components": str(row.get("components","")),
                        "hsk_level": int(row.get("hsk_level",0)),
                        "level": row.get("level",0),
                        "openai_meaning_mnemonic": f"Error: {e}",
                        "openai_reading_mnemonic": f"Error: {e}",
                    }
                    batch.append(res)

                completed += 1
                if len(batch) >= args.batch_size or completed == total:
                    # Append checkpoint
                    append_rows_csv(args.out_hanzi, batch, header=(not header_written_hanzi))
                    header_written_hanzi = True
                    print(f"  ✓ Checkpoint: {completed}/{total} hanzi")
                    batch = []

    # ---------------- Vocabulary ----------------
    print("\n" + "="*70)
    print("📚 Part 3: Vocabulary Mnemonics")
    print("="*70)

    if not os.path.exists(args.out_vocab):
        header_written_vocab = False
    else:
        header_written_vocab = True

    to_process_v = [(i, r) for i, r in vocab_df.iterrows() if str(r["word"]) not in done_vocab]
    total_v = len(to_process_v)
    print(f"→ Pending vocab: {total_v} (skipping {len(vocab_df)-total_v} already done)")

    if total_v:
        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
            futures = []
            for i, row in to_process_v:
                futures.append(ex.submit(generate_vocab_row, client, model, temp_ok, args.rate_delay, row, hanzi_map))

            batch = []
            completed = 0
            for fut in as_completed(futures):
                try:
                    res = fut.result()
                    batch.append(res)
                except Exception as e:
                    res = {
                        "word": str(row.get("word","?")),
                        "pinyin": str(row.get("pinyin","")),
                        "meaning": simple_meaning(str(row.get("meaning",""))),
                        "hanzi_breakdown": "",
                        "hsk_level": int(row.get("hsk_level",0)),
                        "level": row.get("level",0),
                        "openai_meaning_mnemonic": f"Error: {e}",
                        "openai_reading_mnemonic": f"Error: {e}",
                    }
                    batch.append(res)

                completed += 1
                if len(batch) >= args.batch_size or completed == total_v:
                    append_rows_csv(args.out_vocab, batch, header=(not header_written_vocab))
                    header_written_vocab = True
                    print(f"  ✓ Checkpoint: {completed}/{total_v} vocab")
                    batch = []

    # Summary
    print("\n" + "="*70)
    print("✨ Mnemonic Generation Complete!")
    print("="*70)
    print(f"\n📁 Output files:")
    print(f"   🔷 {args.out_radicals}")
    print(f"   📝 {args.out_hanzi}")
    print(f"   📚 {args.out_vocab}")
    if client and not args.dry_run:
        est_items = len(to_process_r) + len(to_process) + len(to_process_v)
        est_tokens = est_items * 350  # rough (radicals use fewer tokens)
        est_cost = est_tokens / 1_000_000 * 0.15  # gpt-4o-mini guide
        print(f"\n💰 Rough cost estimate: ~${est_cost:.2f} (≈{est_tokens:,} tokens)")
    else:
        print("\n⚠️  Placeholders were used (DRY RUN or no API key).")

if __name__ == "__main__":
    main()
