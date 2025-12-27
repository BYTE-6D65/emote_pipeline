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


def reduce_frames(frames: List[Image.Image], durations: List[int], factor: int) -> Tuple[List[Image.Image], List[int]]:
    reduced_frames = frames[::factor]
    reduced_durations = [sum(durations[i:i+factor]) for i in range(0, len(durations), factor)]
    return reduced_frames, reduced_durations


def save_as_gif(animation: Animation, output_path: Path, colors: int = 256, alpha_threshold: int = 10) -> int:
    processed_frames = []

    for frame in animation.frames:
        if frame.mode == "RGBA":
            processed_frames.append(frame)
        else:
            processed_frames.append(frame.convert("RGBA"))

    # Build a single global palette from all frames for consistency
    all_pixels = []
    for frame in processed_frames:
        r, g, b, a = frame.split()
        rgb = Image.merge("RGB", (r, g, b))
        all_pixels.append(rgb)

    # Create palette from first frame, reserve last color for transparency
    palette_img = all_pixels[0].quantize(colors=colors-1, method=Image.Quantize.MEDIANCUT)

    pal_frames = []
    for i, frame in enumerate(processed_frames):
        r, g, b, a = frame.split()
        rgb = Image.merge("RGB", (r, g, b))

        # Quantize to shared palette
        if i == 0:
            p_frame = palette_img
        else:
            p_frame = rgb.quantize(palette=palette_img)

        # Map ONLY fully transparent pixels to transparency index
        # Use lower threshold to preserve semi-transparent outline edges
        p_data = list(p_frame.getdata())
        a_data = list(a.getdata())

        for j, alpha_val in enumerate(a_data):
            if alpha_val < alpha_threshold:
                p_data[j] = colors - 1

        p_frame.putdata(p_data)
        pal_frames.append(p_frame)

    save_kwargs = {
        "save_all": True,
        "append_images": pal_frames[1:],
        "duration": animation.durations,
        "loop": animation.loop,
        "disposal": 2,
        "transparency": colors - 1,
        "optimize": False
    }

    pal_frames[0].save(output_path, **save_kwargs)

    return output_path.stat().st_size


def compress_to_target_size(animation: Animation, output_path: Path, target_size_bytes: int, alpha_threshold: int = 10, min_resolution: int = 1000) -> Path:
    skip_factor = 1
    colors = 256

    # Enforce minimum resolution
    if animation.size[0] < min_resolution or animation.size[1] < min_resolution:
        raise ValueError(f"Input resolution {animation.size} is below minimum {min_resolution}x{min_resolution}")

    while skip_factor <= len(animation.frames) and colors >= 64:
        temp_path = output_path.with_suffix(f".temp{skip_factor}f{colors}c.gif")

        if skip_factor > 1:
            processed_frames, processed_durations = reduce_frames(animation.frames, animation.durations, skip_factor)
        else:
            processed_frames = animation.frames
            processed_durations = animation.durations

        compressed_anim = Animation(
            frames=processed_frames,
            durations=processed_durations,
            loop=animation.loop,
            size=processed_frames[0].size
        )

        size = save_as_gif(compressed_anim, temp_path, colors, alpha_threshold=alpha_threshold)

        if size <= target_size_bytes:
            temp_path.replace(output_path)
            return output_path

        temp_path.unlink()

        skip_factor += 1
        colors = max(64, colors - 32)

    raise RuntimeError(f"Could not compress to target size of {target_size_bytes / (1024 * 1024):.2f} MB")


def main():
    parser = argparse.ArgumentParser(description="Convert animated PNG to web-ready GIF with size constraint")

    # Required arguments
    parser.add_argument("-i", "--input", required=True, type=Path, dest="input_file",
                       help="Input animated PNG file path")
    parser.add_argument("-o", "--output", type=Path,
                       help="Output GIF file path (defaults to input name with .gif extension)")

    # Optional arguments
    parser.add_argument("--max-size", type=float, default=10.0,
                       help="Maximum output size in MB (default: 10.0)")
    parser.add_argument("--alpha-threshold", type=int, default=10,
                       help="Alpha threshold for transparency (0-255). Lower = preserve more semi-transparent pixels (default: 10)")
    parser.add_argument("--min-resolution", type=int, default=1000,
                       help="Minimum required resolution (width and height, default: 1000)")

    args = parser.parse_args()

    if not args.input_file.exists():
        raise FileNotFoundError(f"Input file not found: {args.input_file}")

    output_path = args.output or args.input_file.with_suffix(".gif")

    animation = load_animation(args.input_file)

    target_size_bytes = int(args.max_size * 1024 * 1024)

    result_path = compress_to_target_size(
        animation,
        output_path,
        target_size_bytes,
        alpha_threshold=args.alpha_threshold,
        min_resolution=args.min_resolution
    )

    final_size_mb = result_path.stat().st_size / (1024 * 1024)
    print(f"Successfully created GIF: {result_path}")
    print(f"Final size: {final_size_mb:.2f} MB")
    print(f"Dimensions: {animation.size[0]}x{animation.size[1]}")
    print(f"Frames: {len(animation.frames)}")


if __name__ == "__main__":
    main()
