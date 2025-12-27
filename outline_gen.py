from __future__ import annotations

import argparse
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple
import xml.etree.ElementTree as ET

from PIL import Image, ImageSequence


# ============================================================
# Animation container
# ============================================================

@dataclass
class Animation:
    frames: List[Image.Image]
    durations: List[int]
    loop: int
    size: Tuple[int, int]


# ============================================================
# Padding utility
# ============================================================

def pad_frame(frame: Image.Image, pad: int) -> Image.Image:
    """
    Add transparent padding around the frame to prevent vector outlines
    or silhouette expansions from clipping at canvas edges.
    """
    w, h = frame.size
    padded = Image.new("RGBA", (w + 2*pad, h + 2*pad), (0, 0, 0, 0))
    padded.paste(frame, (pad, pad))
    return padded


# ============================================================
# Load / save PNG/APNG
# ============================================================

def load_animation(path: Path, pad: int) -> Animation:
    """
    Load a PNG/APNG animation and pad every frame by `pad` pixels.
    """
    img = Image.open(path)

    if img.format != "PNG":
        raise ValueError(f"Unsupported format: {img.format}")

    base_w, base_h = img.size
    frames: List[Image.Image] = []
    durations: List[int] = []

    for frame in ImageSequence.Iterator(img):
        rgba = frame.convert("RGBA")

        # Normalize to master canvas
        canvas = Image.new("RGBA", (base_w, base_h), (0, 0, 0, 0))
        canvas.paste(rgba, (0, 0))

        # Apply padding (important)
        padded = pad_frame(canvas, pad)
        frames.append(padded)

        durations.append(frame.info.get("duration",
                        img.info.get("duration", 40)))

    loop = img.info.get("loop", 0)

    padded_size = (base_w + 2*pad, base_h + 2*pad)

    return Animation(
        frames=frames,
        durations=durations,
        loop=loop,
        size=padded_size,
    )


def save_animation(anim: Animation, output_path: Path) -> None:
    """
    Save frames back to PNG/APNG.
    """
    first, *rest = anim.frames

    first.save(
        output_path,
        format="PNG",
        save_all=True,
        append_images=rest,
        duration=anim.durations,
        loop=anim.loop,
        disposal=2,
    )


# ============================================================
# Scaling utility
# ============================================================

def scale_frame(frame: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
    """
    Scale a frame to the target size using high-quality resampling.
    """
    return frame.resize(target_size, Image.Resampling.LANCZOS)


# ============================================================
# Silhouette extraction (no dilation - stroke width handles extension)
# ============================================================

def extract_silhouette_mask(frame: Image.Image, alpha_threshold: int = 10) -> Image.Image:
    """
    Binary silhouette mask from alpha channel.
    No dilation needed - the SVG stroke width naturally extends the outline.
    """
    rgba = frame.convert("RGBA")

    # Extract alpha channel and threshold it
    alpha = rgba.getchannel("A")

    # Create lookup table for thresholding: 255 where value > threshold, 0 otherwise
    lut = [255 if i > alpha_threshold else 0 for i in range(256)]
    mask = alpha.point(lut)

    return mask


def mask_to_pbm(mask: Image.Image, path: Path) -> None:
    """
    Convert 8-bit mask to PBM for potrace.
    PBM: 0=black, 1=white -> invert mask so silhouette=black (what potrace traces).
    """
    inverted = mask.point(lambda p: 0 if p > 0 else 255)
    binary = inverted.convert("1")
    binary.save(path, format="PPM")  # Pillow handles PBM/PPM appropriately


# ============================================================
# External tools: Potrace + Inkscape 1.4.x
# ============================================================

def run_potrace(pbm_path: Path, svg_path: Path) -> None:
    """
    Run potrace with optimized settings:
      --flat: process each connected component separately (prevents island bridging)
      --opttolerance 0.3: balance between smoothness and accuracy

    NOTE: We do NOT use --tight because it crops the canvas and breaks coordinate mapping.
    The SVG must preserve the full image dimensions for 1:1 alignment with the raster.
    """
    cmd = [
        "potrace",
        str(pbm_path),
        "--svg",
        "-o", str(svg_path),
        "--flat",
        "--opttolerance", "0.3",
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Potrace failed: {e.stderr}") from e


def edit_svg_add_outline(
    svg_path: Path,
    outline_rgba: Tuple[int, int, int, int],
    stroke_width_px: float,
) -> None:
    """
    Modify SVG: apply stroke to all <path> elements.
    Uses round joins and caps for smooth outline appearance.
    The stroke extends outward from the silhouette edge.
    """
    r, g, b, a = outline_rgba
    stroke = f"rgb({r},{g},{b})"
    opacity = a / 255.0

    tree = ET.parse(svg_path)
    root = tree.getroot()

    ns = {"svg": "http://www.w3.org/2000/svg"}
    ET.register_namespace("", ns["svg"])

    path_count = 0
    for path in root.findall(".//svg:path", ns):
        path.set("fill", "none")
        path.set("stroke", stroke)
        path.set("stroke-width", str(stroke_width_px))
        path.set("stroke-opacity", str(opacity))
        path.set("stroke-linejoin", "round")
        path.set("stroke-linecap", "round")
        path_count += 1

    if path_count == 0:
        raise RuntimeError(f"No paths found in SVG: {svg_path}")

    tree.write(svg_path, encoding="utf-8", xml_declaration=True)


def rasterize_svg_with_inkscape(
    svg_path: Path,
    png_path: Path,
    target_size: Tuple[int, int],
) -> None:
    """
    Inkscape 1.4+ syntax:
      inkscape input.svg --export-type=png --export-filename out.png \
                         --export-width W --export-height H
    """
    w, h = target_size

    cmd = [
        "inkscape",
        str(svg_path),
        "--export-type=png",
        "--export-filename", str(png_path),
        "--export-width", str(w),
        "--export-height", str(h),
        "--export-background-opacity=0",
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Inkscape failed: {e.stderr}") from e

    if not png_path.exists():
        raise RuntimeError(f"Inkscape did not create output file: {png_path}")


# ============================================================
# Per-frame processing with correct architecture
# ============================================================

def process_frame(
    frame: Image.Image,
    target_size: Tuple[int, int],
    outline_color_rgba: Tuple[int, int, int, int],
    outline_width_px: float,
    tmp_dir: Path,
    index: int,
) -> Image.Image:
    """
    Process a single frame with the correct architecture:
    1. Scale to target size FIRST
    2. Extract silhouette mask from scaled image
    3. Vectorize at target resolution with --flat (handles islands separately)
    4. Apply stroke to SVG paths
    5. Rasterize SVG back to PNG
    6. Composite outline UNDER the scaled original
    """

    # Step 1: Scale to target size FIRST
    scaled_frame = scale_frame(frame, target_size).convert("RGBA")

    # Step 2: Extract silhouette mask from SCALED image (no dilation)
    mask = extract_silhouette_mask(scaled_frame)

    # Step 3: Convert mask to PBM for potrace
    pbm = tmp_dir / f"f{index:04d}.pbm"
    svg = tmp_dir / f"f{index:04d}.svg"
    outline_png = tmp_dir / f"f{index:04d}_outline.png"

    mask_to_pbm(mask, pbm)

    # Step 4: Vectorize at target resolution with --flat flag
    run_potrace(pbm, svg)

    # Step 5: Apply SVG stroke (extends naturally beyond silhouette edge)
    edit_svg_add_outline(svg, outline_color_rgba, outline_width_px)

    # Step 6: Rasterize outline SVG back to PNG at target size
    rasterize_svg_with_inkscape(svg, outline_png, target_size)
    outline_img = Image.open(outline_png).convert("RGBA")

    # Step 7: Composite outline UNDER the scaled original
    # outline_img is the background, scaled_frame goes on top
    final = Image.alpha_composite(outline_img, scaled_frame)

    return final


def run_pipeline(
    anim: Animation,
    target_size: Tuple[int, int],
    outline_color_rgba: Tuple[int, int, int, int],
    outline_width_px: float,
) -> Animation:
    """
    Process all frames through the vector outline pipeline.
    """
    output_frames = []
    total_frames = len(anim.frames)

    print(f"Processing {total_frames} frame{'s' if total_frames != 1 else ''}...")

    with tempfile.TemporaryDirectory() as tmpd:
        tmp_dir = Path(tmpd)

        for idx, frame in enumerate(anim.frames):
            print(f"  Frame {idx+1}/{total_frames}...", end=" ", flush=True)

            out = process_frame(
                frame=frame,
                target_size=target_size,
                outline_color_rgba=outline_color_rgba,
                outline_width_px=outline_width_px,
                tmp_dir=tmp_dir,
                index=idx,
            )
            output_frames.append(out)
            print("done")

    return Animation(
        frames=output_frames,
        durations=anim.durations,
        loop=anim.loop,
        size=target_size,
    )


# ============================================================
# CLI interface
# ============================================================

def parse_color(value: str) -> Tuple[int, int, int, int]:
    v = value.strip()
    if v.startswith("#"):
        v = v[1:]
    if len(v) != 6:
        raise argparse.ArgumentTypeError("Color must be RRGGBB")
    return (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16), 255)


def parse_args():
    p = argparse.ArgumentParser("Hybrid Emote Vector Pipeline")
    p.add_argument("-i", "--input", required=True,
                   help="Input PNG/APNG file")
    p.add_argument("-o", "--output", required=True,
                   help="Output PNG/APNG file")
    p.add_argument("-s", "--size", type=int, default=1000,
                   help="Target output size (square, default 1000)")
    p.add_argument("-c", "--color", type=parse_color, default=(255, 255, 255, 255),
                   help="Outline color in RRGGBB hex (default: FFFFFF for white)")
    p.add_argument("-w", "--width", type=float, default=6.0,
                   help="Outline stroke width in pixels (default 6.0)")
    p.add_argument("--pad", type=int, default=80,
                   help="Padding added to frames before processing (default 80px)")
    return p.parse_args()


def main():
    args = parse_args()

    inp = Path(args.input)
    out = Path(args.output)
    target = (args.size, args.size)

    if not inp.exists():
        raise FileNotFoundError(f"Input file not found: {inp}")

    print(f"Input: {inp}")
    print(f"Output: {out}")
    print(f"Target size: {args.size}x{args.size}")
    print(f"Outline: {args.width}px, color=#{args.color[0]:02x}{args.color[1]:02x}{args.color[2]:02x}")
    print(f"Padding: {args.pad}px")
    print()

    anim = load_animation(inp, pad=args.pad)
    print(f"Loaded {len(anim.frames)} frame(s), padded size: {anim.size}")
    print()

    processed = run_pipeline(
        anim=anim,
        target_size=target,
        outline_color_rgba=args.color,
        outline_width_px=args.width,
    )

    print()
    print("Saving animation...")
    save_animation(processed, out)

    output_size_mb = out.stat().st_size / (1024 * 1024)
    print(f"Complete! Output: {out}")
    print(f"  Size: {output_size_mb:.2f} MB")
    print(f"  Canvas: {processed.size[0]}x{processed.size[1]}")
    print(f"  Frames: {len(processed.frames)}")


if __name__ == "__main__":
    main()
