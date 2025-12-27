#!/usr/bin/env python3
"""
Emote Pipeline - Automated workflow for creating web-ready animated emotes

This tool orchestrates the complete pipeline:
1. Add vector outline (outline_gen.py)
2. Resize to target dimensions (image_resize.py)
3. Convert to optimized GIF (apng_to_gif.py)
"""

from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


def run_command(cmd: list[str], description: str) -> None:
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"STEP: {description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(str(c) for c in cmd)}\n")

    result = subprocess.run(cmd, capture_output=False, text=True)

    if result.returncode != 0:
        print(f"\n❌ Failed at step: {description}", file=sys.stderr)
        sys.exit(1)

    print(f"✓ {description} complete")


def main():
    parser = argparse.ArgumentParser(
        description="Automated emote pipeline: outline → resize → GIF optimization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline with defaults (white outline, 1000px, 10MB GIF)
  %(prog)s -i tail.png -o output.gif

  # Custom outline color and width
  %(prog)s -i tail.png -o output.gif -c FF0000 -w 8.0

  # Smaller output for Discord
  %(prog)s -i tail.png -o discord.gif -s 512 --max-size 0.25

  # Skip steps (e.g., already have outline)
  %(prog)s -i outlined.png -o output.gif --skip-outline

  # Keep intermediate files
  %(prog)s -i tail.png -o output.gif --keep-temp
"""
    )

    # Input/Output
    parser.add_argument("-i", "--input", required=True, type=Path,
                       help="Input PNG/APNG file")
    parser.add_argument("-o", "--output", required=True, type=Path,
                       help="Output GIF file path")

    # Outline parameters
    outline_group = parser.add_argument_group("outline generation")
    outline_group.add_argument("-c", "--color", default="FFFFFF",
                              help="Outline color in hex RRGGBB (default: FFFFFF = white)")
    outline_group.add_argument("-w", "--width", type=float, default=6.0,
                              help="Outline stroke width in pixels (default: 6.0)")
    outline_group.add_argument("--pad", type=int, default=80,
                              help="Padding around frames in pixels (default: 80)")

    # Resize parameters
    resize_group = parser.add_argument_group("resize")
    resize_group.add_argument("-s", "--size", type=int, default=1000,
                             help="Target output size (square, default: 1000)")

    # GIF optimization parameters
    gif_group = parser.add_argument_group("GIF optimization")
    gif_group.add_argument("--max-size", type=float, default=10.0,
                          help="Maximum GIF size in MB (default: 10.0)")

    # Pipeline control
    control_group = parser.add_argument_group("pipeline control")
    control_group.add_argument("--skip-outline", action="store_true",
                              help="Skip outline generation (input already has outline)")
    control_group.add_argument("--skip-resize", action="store_true",
                              help="Skip resize step (input already correct size)")
    control_group.add_argument("--skip-gif", action="store_true",
                              help="Skip GIF conversion (output APNG only)")
    control_group.add_argument("--keep-temp", action="store_true",
                              help="Keep intermediate files (for debugging)")
    control_group.add_argument("--temp-dir", type=Path,
                              help="Custom directory for intermediate files (default: same as output)")

    args = parser.parse_args()

    # Validate input
    if not args.input.exists():
        print(f"❌ Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Get script directory
    script_dir = Path(__file__).parent

    # Setup temp directory
    if args.temp_dir:
        temp_dir = args.temp_dir
        temp_dir.mkdir(parents=True, exist_ok=True)
    else:
        temp_dir = args.output.parent

    # Define intermediate file paths with timestamp to prevent collisions
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outlined_path = temp_dir / f"{args.input.stem}_outlined_{timestamp}.png"
    resized_path = temp_dir / f"{args.input.stem}_resized_{timestamp}.png"

    print("\n" + "="*60)
    print("EMOTE PIPELINE")
    print("="*60)
    print(f"Input:  {args.input}")
    print(f"Output: {args.output}")
    print(f"Steps:  {'outline' if not args.skip_outline else 'skip-outline'} → "
          f"{'resize' if not args.skip_resize else 'skip-resize'} → "
          f"{'GIF' if not args.skip_gif else 'APNG'}")

    current_file = args.input

    # STEP 1: Generate outline at NATIVE resolution (no scaling yet)
    if not args.skip_outline:
        # Get native size of input to pass to outline_gen
        from PIL import Image
        with Image.open(current_file) as img:
            native_w, native_h = img.size

        # Add padding to native size
        padded_size = native_w + 2 * args.pad

        cmd = [
            sys.executable,
            str(script_dir / "outline_gen.py"),
            "-i", str(current_file),
            "-o", str(outlined_path),
            "-s", str(padded_size),  # Use native+padding size, NOT target size
            "-c", args.color,
            "-w", str(args.width),
            "--pad", str(args.pad),
        ]
        run_command(cmd, "Generate vector outline at native resolution")
        current_file = outlined_path

    # STEP 2: Resize
    if not args.skip_resize:
        cmd = [
            sys.executable,
            str(script_dir / "image_resize.py"),
            "-i", str(current_file),
            "-o", str(resized_path),
            "-s", str(args.size),
        ]
        run_command(cmd, "Resize to target dimensions")
        current_file = resized_path

    # STEP 3: Convert to GIF
    if not args.skip_gif:
        cmd = [
            sys.executable,
            str(script_dir / "apng_to_gif.py"),
            "-i", str(current_file),
            "-o", str(args.output),
            "--max-size", str(args.max_size),
        ]
        run_command(cmd, "Optimize and convert to GIF")
    else:
        # Just copy the APNG to output
        import shutil
        shutil.copy(current_file, args.output)
        print(f"\n✓ Copied APNG to {args.output}")

    # Cleanup intermediate files
    if not args.keep_temp:
        print(f"\n{'='*60}")
        print("Cleaning up intermediate files...")
        print(f"{'='*60}")

        if outlined_path.exists() and outlined_path != args.input:
            outlined_path.unlink()
            print(f"Removed: {outlined_path}")

        if resized_path.exists() and resized_path != args.input:
            resized_path.unlink()
            print(f"Removed: {resized_path}")

    # Final summary
    print(f"\n{'='*60}")
    print("✓ PIPELINE COMPLETE")
    print(f"{'='*60}")
    print(f"Output: {args.output}")

    if args.output.exists():
        size_mb = args.output.stat().st_size / (1024 * 1024)
        print(f"Size:   {size_mb:.2f} MB")

    if args.keep_temp:
        print(f"\nIntermediate files saved in: {temp_dir}")
        if outlined_path.exists():
            print(f"  - {outlined_path}")
        if resized_path.exists():
            print(f"  - {resized_path}")


if __name__ == "__main__":
    main()
