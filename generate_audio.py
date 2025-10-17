#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate audio files for hanzi and vocabulary using OpenAI TTS API.

This script generates high-quality MP3 audio files for:
1. Hanzi characters - pronunciation with pinyin
2. Vocabulary words - pronunciation with pinyin

Audio files are saved in:
- data/audio/hanzi/{hanzi}.mp3
- data/audio/vocabulary/{word}.mp3
"""

from __future__ import annotations

import argparse
import io
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock
from typing import Optional

# Windows console UTF-8 setup
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    import pandas as pd
    from dotenv import load_dotenv
    from openai import OpenAI
    from tqdm import tqdm
except ImportError as exc:
    print(f"Dependency error: {exc}")
    print("\nInstall missing packages with:")
    print("  pip install pandas pyarrow python-dotenv tqdm openai")
    sys.exit(1)


# Global lock for thread-safe progress bar updates
_progress_lock = Lock()


def load_env(env_name: str = ".env") -> None:
    """Load environment variables from a local .env file."""
    env_path = Path(__file__).parent / env_name
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Loaded environment from {env_path}")
    else:
        print(f"⚠️  No .env file found at {env_path}")
        print("   You can copy .env.example to configure local secrets.")


def init_openai_client() -> Optional[OpenAI]:
    """Create an OpenAI client if an API key is available."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        print("❌ OPENAI_API_KEY not set. Cannot generate audio.")
        print("   Please set your API key in .env file")
        return None
    return OpenAI()


def sanitize_filename(text: str) -> str:
    """Sanitize text for use as a filename.
    
    Removes or replaces characters that are invalid in filenames.
    """
    # Replace problematic characters
    replacements = {
        '/': '_',
        '\\': '_',
        ':': '_',
        '*': '_',
        '?': '_',
        '"': '_',
        '<': '_',
        '>': '_',
        '|': '_',
        ' ': '_',
    }
    
    result = text
    for old, new in replacements.items():
        result = result.replace(old, new)
    
    return result


def generate_audio_file(
    client: OpenAI,
    text: str,
    output_path: Path,
    voice: str = "alloy",
    model: str = "gpt-4o-mini-tts",
    speed: float = 1,
    instructions: str = None,
) -> bool:
    """Generate an audio file using OpenAI TTS endpoint with instructions support.
    
    Args:
        client: OpenAI client instance
        text: Text to convert to speech
        output_path: Path where to save the MP3 file
        voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
        model: Model to use (gpt-4o-mini-tts supports instructions)
        speed: Speed of speech (0.25 to 4.0)
        instructions: Optional pronunciation instructions for the model
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create parent directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Default instructions for Mandarin teaching style
        if instructions is None:
            instructions = (
                "Language: Mandarin (Putonghua). Style: calm, clear, friendly. "
                "Pacing: slow and clearly articulated; small pauses between words; longer pauses between clauses. "
                "Diction: enunciate initials/finals cleanly; make tones distinct (1=high-level, 2=rising, 3=low-dipping, 4=falling). "
                "Standard Beijing-neutral pronunciation."
            )
        
        # Generate audio using TTS endpoint with instructions
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            speed=speed,
            instructions=instructions,  # Pass instructions to the model
        )
        
        # Save audio to file
        output_path.write_bytes(response.content)
        return True
        
    except Exception as exc:
        print(f"❌ Error generating audio for '{text}': {exc}")
        return False


def _generate_single_audio(
    client: OpenAI,
    text: str,
    output_path: Path,
    voice: str,
    model: str,
    speed: float,
    skip_existing: bool,
) -> bool:
    """Generate a single audio file (thread-safe helper function)."""
    # Skip if file exists
    if skip_existing and output_path.exists():
        return True
    
    # Generate audio
    return generate_audio_file(
        client=client,
        text=text,
        output_path=output_path,
        voice=voice,
        model=model,
        speed=speed,
    )


def generate_hanzi_audio(
    client: OpenAI,
    data_path: Path,
    output_dir: Path,
    voice: str = "verse",
    model: str = "gpt-4o-mini-tts",
    speed: float = 1,
    skip_existing: bool = True,
    limit: Optional[int] = None,
    max_workers: int = 5,
) -> tuple[int, int]:
    """Generate audio files for all hanzi characters.
    
    Args:
        client: OpenAI client instance
        data_path: Path to hanzi.csv file
        output_dir: Directory to save audio files
        voice: Voice to use for TTS
        model: TTS model to use
        speed: Speech speed
        skip_existing: Skip files that already exist
        limit: Optional limit on number of files to generate
        max_workers: Maximum number of parallel threads (default: 5)
    
    Returns:
        Tuple of (successful_count, total_count)
    """
    print(f"\n{'='*60}")
    print("🎵 Generating Hanzi Audio Files")
    print(f"{'='*60}")
    
    # Load hanzi data
    if not data_path.exists():
        print(f"❌ Hanzi data file not found: {data_path}")
        return 0, 0
    
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} hanzi characters from {data_path}")
    
    if limit:
        df = df.head(limit)
        print(f"⚠️  Limited to first {limit} characters for testing")
    
    print(f"Using {max_workers} parallel threads")
    
    # Prepare tasks
    tasks = []
    for _, row in df.iterrows():
        hanzi = row['hanzi']
        safe_filename = sanitize_filename(hanzi)
        output_path = output_dir / f"{safe_filename}.mp3"
        
        tasks.append({
            'text': hanzi,
            'output_path': output_path,
        })
    
    # Execute in parallel with progress bar
    successful = 0
    total = len(tasks)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        futures = {
            executor.submit(
                _generate_single_audio,
                client,
                task['text'],
                task['output_path'],
                voice,
                model,
                speed,
                skip_existing,
            ): task for task in tasks
        }
        
        # Process completed tasks with progress bar
        with tqdm(total=total, desc="Generating hanzi audio") as pbar:
            for future in as_completed(futures):
                try:
                    if future.result():
                        successful += 1
                except Exception as exc:
                    task = futures[future]
                    print(f"\n❌ Error processing {task['text']}: {exc}")
                finally:
                    pbar.update(1)
    
    print(f"\n✓ Generated {successful}/{total} hanzi audio files")
    print(f"  Output directory: {output_dir}")
    
    return successful, total


def generate_vocabulary_audio(
    client: OpenAI,
    data_path: Path,
    output_dir: Path,
    voice: str = "verse",
    model: str = "gpt-4o-mini-tts",
    speed: float = 1,
    skip_existing: bool = True,
    limit: Optional[int] = None,
    max_workers: int = 5,
) -> tuple[int, int]:
    """Generate audio files for all vocabulary words.
    
    Args:
        client: OpenAI client instance
        data_path: Path to vocabulary.csv file
        output_dir: Directory to save audio files
        voice: Voice to use for TTS
        model: TTS model to use
        speed: Speech speed
        skip_existing: Skip files that already exist
        limit: Optional limit on number of files to generate
        max_workers: Maximum number of parallel threads (default: 5)
    
    Returns:
        Tuple of (successful_count, total_count)
    """
    print(f"\n{'='*60}")
    print("🎵 Generating Vocabulary Audio Files")
    print(f"{'='*60}")
    
    # Load vocabulary data
    if not data_path.exists():
        print(f"❌ Vocabulary data file not found: {data_path}")
        return 0, 0
    
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} vocabulary words from {data_path}")
    
    if limit:
        df = df.head(limit)
        print(f"⚠️  Limited to first {limit} words for testing")
    
    print(f"Using {max_workers} parallel threads")
    
    # Prepare tasks
    tasks = []
    for _, row in df.iterrows():
        word = row['word']
        safe_filename = sanitize_filename(word)
        output_path = output_dir / f"{safe_filename}.mp3"
        
        tasks.append({
            'text': word,
            'output_path': output_path,
        })
    
    # Execute in parallel with progress bar
    successful = 0
    total = len(tasks)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        futures = {
            executor.submit(
                _generate_single_audio,
                client,
                task['text'],
                task['output_path'],
                voice,
                model,
                speed,
                skip_existing,
            ): task for task in tasks
        }
        
        # Process completed tasks with progress bar
        with tqdm(total=total, desc="Generating vocab audio") as pbar:
            for future in as_completed(futures):
                try:
                    if future.result():
                        successful += 1
                except Exception as exc:
                    task = futures[future]
                    print(f"\n❌ Error processing {task['text']}: {exc}")
                finally:
                    pbar.update(1)
    
    print(f"\n✓ Generated {successful}/{total} vocabulary audio files")
    print(f"  Output directory: {output_dir}")
    
    return successful, total


def main() -> None:
    """Main entry point for the audio generation pipeline."""
    parser = argparse.ArgumentParser(
        description="Generate audio files for hanzi and vocabulary using OpenAI TTS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all audio files
  python generate_audio.py --all
  
  # Generate only hanzi audio
  python generate_audio.py --hanzi
  
  # Generate only vocabulary audio
  python generate_audio.py --vocabulary
  
  # Test with first 10 items only
  python generate_audio.py --all --limit 10
  
  # Use a different voice
  python generate_audio.py --all --voice shimmer
  
  # Use standard quality (faster, cheaper)
  python generate_audio.py --all --model tts-1
  
  # Force regenerate all files
  python generate_audio.py --all --no-skip-existing
        """
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate both hanzi and vocabulary audio files"
    )
    parser.add_argument(
        "--hanzi",
        action="store_true",
        help="Generate hanzi audio files only"
    )
    parser.add_argument(
        "--vocabulary",
        action="store_true",
        help="Generate vocabulary audio files only"
    )
    parser.add_argument(
        "--voice",
        type=str,
        default="alloy",
        choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        help="Voice to use for audio generation (default: alloy)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini-tts",
        choices=["gpt-4o-mini-tts"],
        help="TTS model to use (default: gpt-4o-mini-tts supports instructions)"
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Speech speed, 0.25 to 4.0 (default: 1.0 - normal speed)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of files to generate (for testing)"
    )
    parser.add_argument(
        "--no-skip-existing",
        action="store_true",
        help="Regenerate all files, even if they exist"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=5,
        help="Number of parallel threads (default: 5, increase for faster generation)"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Directory containing data files (default: data)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/audio"),
        help="Base directory for audio output (default: data/audio)"
    )
    
    args = parser.parse_args()
    
    # If no specific option is set, default to --all
    if not (args.all or args.hanzi or args.vocabulary):
        args.all = True
    
    # Load environment variables
    load_env()
    
    # Initialize OpenAI client
    client = init_openai_client()
    if client is None:
        print("\n❌ Cannot proceed without OpenAI API key")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print("🎵 OpenAI Audio Generation Pipeline")
    print(f"{'='*60}")
    print(f"Voice: {args.voice}")
    print(f"Model: {args.model}")
    print(f"Speed: {args.speed}x")
    print(f"Parallel threads: {args.workers}")
    print(f"Skip existing: {not args.no_skip_existing}")
    if args.limit:
        print(f"Limit: {args.limit} items")
    
    total_success = 0
    total_count = 0
    
    # Generate hanzi audio
    if args.all or args.hanzi:
        hanzi_path = args.data_dir / "hanzi.csv"
        hanzi_output = args.output_dir / "hanzi"
        
        success, count = generate_hanzi_audio(
            client=client,
            data_path=hanzi_path,
            output_dir=hanzi_output,
            voice=args.voice,
            model=args.model,
            speed=args.speed,
            skip_existing=not args.no_skip_existing,
            limit=args.limit,
            max_workers=args.workers,
        )
        total_success += success
        total_count += count
    
    # Generate vocabulary audio
    if args.all or args.vocabulary:
        vocab_path = args.data_dir / "vocabulary.csv"
        vocab_output = args.output_dir / "vocabulary"
        
        success, count = generate_vocabulary_audio(
            client=client,
            data_path=vocab_path,
            output_dir=vocab_output,
            voice=args.voice,
            model=args.model,
            speed=args.speed,
            skip_existing=not args.no_skip_existing,
            limit=args.limit,
            max_workers=args.workers,
        )
        total_success += success
        total_count += count
    
    # Final summary
    print(f"\n{'='*60}")
    print("✅ Audio Generation Complete!")
    print(f"{'='*60}")
    print(f"Total: {total_success}/{total_count} files generated successfully")
    
    if total_success < total_count:
        print(f"⚠️  {total_count - total_success} files failed to generate")
        sys.exit(1)


if __name__ == "__main__":
    main()
