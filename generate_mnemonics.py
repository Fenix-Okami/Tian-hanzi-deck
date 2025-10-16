#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrapper CLI that dispatches to the dedicated mnemonic generators."""

from __future__ import annotations

import argparse
from typing import List, Optional, Set

from mnemonic_common import OpenAI, load_env

import generate_hanzi_mnemonics as hanzi_module
import generate_radical_mnemonics as radical_module
import generate_vocab_mnemonics as vocab_module

DEFAULT_MODEL = "gpt-5"
DEFAULT_RADICALS_IN = "data/radicals_tian.csv"
DEFAULT_HANZI_IN = "data/hanzi.csv"
DEFAULT_VOCAB_IN = "data/vocabulary.csv"
DEFAULT_RADICALS_OUT = "data/radicals_mnemonic.csv"
DEFAULT_HANZI_OUT = "data/hanzi_mnemonic.csv"
DEFAULT_VOCAB_OUT = "data/vocabulary_mnemonic.csv"
DEFAULT_BATCH_SIZE = 10
DEFAULT_WORKERS = 6
DEFAULT_RATE_DELAY = 0.4
DEFAULT_RESUME = False


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="HSK mnemonic generator (wrapper)")
    parser.add_argument(
        "--deck",
        default="all",
        choices=["all", "radicals", "hanzi", "vocab"],
        help="Choose which deck to generate.",
    )
    parser.add_argument("--test-mode", action="store_true", help="Limit run to the first 5 rows for a quick check.")
    return parser


def parse_types(raw: str) -> Set[str]:
    if raw.lower() == "all":
        return {"radicals", "hanzi", "vocab"}
    return {raw.lower()}


def run_radicals(args: argparse.Namespace, client: Optional[OpenAI]) -> Optional[OpenAI]:
    rad_args = argparse.Namespace(
        model=DEFAULT_MODEL,
        radicals=DEFAULT_RADICALS_IN,
        out=DEFAULT_RADICALS_OUT,
        batch_size=DEFAULT_BATCH_SIZE,
        workers=DEFAULT_WORKERS,
        rate_delay=DEFAULT_RATE_DELAY,
        dry_run=args.dry_run,
        test_mode=args.test_mode,
        resume=DEFAULT_RESUME,
    )
    return radical_module.run(rad_args, client)


def run_hanzi(args: argparse.Namespace, client: Optional[OpenAI]) -> Optional[OpenAI]:
    hanzi_args = argparse.Namespace(
        model=DEFAULT_MODEL,
        hanzi=DEFAULT_HANZI_IN,
        radicals=DEFAULT_RADICALS_IN,
        out=DEFAULT_HANZI_OUT,
        batch_size=DEFAULT_BATCH_SIZE,
        workers=DEFAULT_WORKERS,
        rate_delay=DEFAULT_RATE_DELAY,
        dry_run=args.dry_run,
        test_mode=args.test_mode,
        resume=DEFAULT_RESUME,
    )
    return hanzi_module.run(hanzi_args, client)


def run_vocab(args: argparse.Namespace, client: Optional[OpenAI]) -> Optional[OpenAI]:
    vocab_args = argparse.Namespace(
        model=DEFAULT_MODEL,
        vocab=DEFAULT_VOCAB_IN,
        hanzi=DEFAULT_HANZI_IN,
        hanzi_mnemonic=DEFAULT_HANZI_OUT,
        out=DEFAULT_VOCAB_OUT,
        batch_size=DEFAULT_BATCH_SIZE,
        workers=DEFAULT_WORKERS,
        rate_delay=DEFAULT_RATE_DELAY,
        dry_run=args.dry_run,
        test_mode=args.test_mode,
        resume=DEFAULT_RESUME,
    )
    return vocab_module.run(vocab_args, client)


def main(argv: Optional[List[str]] = None) -> None:
    args = build_parser().parse_args(argv)
    load_env()

    selected = parse_types(args.deck)
    if not selected:
        print("No generator selected. Choose one of: all, radicals, hanzi, vocab.")
        return

    print(f"Running generators: {', '.join(sorted(selected))} (model: {DEFAULT_MODEL})")

    client: Optional[OpenAI] = None
    args.dry_run = False

    from mnemonic_common import init_openai_client

    client = init_openai_client()
    if client is None:
        print("OpenAI client could not be initialized. Continuing in dry-run mode.")
        args.dry_run = True

    if "radicals" in selected:
        client = run_radicals(args, client)

    if "hanzi" in selected:
        client = run_hanzi(args, client)

    if "vocab" in selected:
        client = run_vocab(args, client)

    print("All requested generators have finished.")


if __name__ == "__main__":
    main()
