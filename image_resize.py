from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple
import argparse

from PIL import Image, ImageSequence


@dataclass
class Animation:
    frames: List[Image.Image]
    durations: List[int]
    loop: int
    size: Tuple[int, int]


def load_animation(path: Path) -> Animation:
    img = Image.open(path)

    if img.format != "PNG":
        raise ValueError(f"Unsupported format: {img.format}")

    frames: list[Image.Image] = []
    durations: list[int] = []

    for frame in ImageSequence.Iterator(img):
        frames.append(frame.convert("RGBA"))
        durations.append(frame.info.get("duration", img.info.get("duration", 40)))

    if not frames:
        raise RuntimeError("Image contained no frames.")

    size = frames[0].size
    loop = img.info.get("loop", 0)

    return Animation(
        frames=frames,
        durations=durations,
        loop=loop,
        size=size
    )


def resize_animation(anim: Animation, target_size: Tuple[int, int]) -> Animation:
    resized = [
        frame.resize(target_size, Image.Resampling.LANCZOS)
        for frame in anim.frames
    ]

    return Animation(
        frames=resized,
        durations=anim.durations,
        loop=anim.loop,
        size=target_size
    )


def save_animation(anim: Animation, output_path: Path) -> None:
    first, *rest = anim.frames

    first.save(
        output_path,
        format="PNG",
        save_all=True,
        append_images=rest,
        duration=anim.durations,
        loop=anim.loop,
        disposal=2
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Resize static or animated PNGs.")
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to input PNG/APNG file"
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Output file path OR directory"
    )
    parser.add_argument(
        "--size",
        "-s",
        type=int,
        default=1000,
        help="Target size (width=height), default = 1000"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    input_path = Path(args.input)
    output_arg = Path(args.output)
    target_size = (args.size, args.size)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Allow user to pass a directory as output target
    if output_arg.is_dir():
        output_path = output_arg / input_path.name
    else:
        output_path = output_arg

    anim = load_animation(input_path)
    resized = resize_animation(anim, target_size)
    save_animation(resized, output_path)

    print(f"Resized {len(anim.frames)} frame(s) from {anim.size} → {resized.size}")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()